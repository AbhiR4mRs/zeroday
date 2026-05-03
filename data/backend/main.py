from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis
import json
import numpy as np
import asyncio
from collections import deque
from pathlib import Path
import joblib

from data.backend.model_loader import ZeroDayDetector
from data.src.data_preparation.config import WINDOW_SIZE, FEATURES
from data.src.llm_analysis.feature_deviation import compute_feature_deviation
from data.src.llm_analysis.prompt_builder import build_prompt
from data.src.llm_analysis.llm_engine import run_llm


app = FastAPI(title="Zero-Day IDS Real-Time")

# Async Redis client
r = aioredis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

detector = ZeroDayDetector()


# Inline explain_window function (no import issues)
def explain_window(window_array: np.ndarray) -> str:
    BASE_DIR = Path(__file__).resolve().parents[2]
    X_TRAIN_PATH = BASE_DIR / "data" / "processed" / "X_train.npy"
    
    # Precompute benign mean once
    benign_mean = np.load(X_TRAIN_PATH).mean(axis=(0, 1))
    
    deviation = compute_feature_deviation(
        window_array=window_array,
        benign_mean=benign_mean,
        feature_names=FEATURES,
    )
    
    prompt = build_prompt(deviation)
    explanation = run_llm(prompt)
    return explanation


@app.get("/")
def health():
    return {"status": "running"}


@app.websocket("/ws/traffic/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    traffic_window = deque(maxlen=WINDOW_SIZE)

    try:
        while True:
            res = await r.brpop("network_traffic_queue")
            if not res:
                continue

            _, data = res
            flow = json.loads(data)

            if len(flow) != len(FEATURES):
                continue

            traffic_window.append(flow)

            if len(traffic_window) < WINDOW_SIZE:
                continue

            window_array = np.array(traffic_window, dtype=float)

            # Run model in thread
            score, is_anomaly = await asyncio.to_thread(
                detector.predict, window_array
            )

            explanation = "Normal traffic."
            if is_anomaly:
                try:
                    explanation = await asyncio.wait_for(
                        asyncio.to_thread(explain_window, window_array),
                        timeout=8.0,
                    )
                except asyncio.TimeoutError:
                    explanation = "Anomaly detected, but LLM explanation timed out."
                except Exception as e:
                    explanation = f"Anomaly detected, explanation error: {str(e)[:100]}"

            payload = {
                "timestamp": str(np.datetime64("now")),
                "score": float(score),
                "status": "CRITICAL" if is_anomaly else "NORMAL",
                "explanation": explanation,
            }

            await websocket.send_json(payload)

    except WebSocketDisconnect:
        print("🔌 Client disconnected from WebSocket.")
    except Exception as e:
        print(f"⚠️ WebSocket loop error: {e}")
        await websocket.close()
