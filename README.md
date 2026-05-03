# Zero-Day Intrusion Detection System using TFT and Autoencoder

A real-time network intrusion detection system that learns normal traffic patterns and flags suspicious behavior using reconstruction error. The project combines an attention-based sequence model, anomaly scoring, explanation generation, and a live monitoring pipeline for detecting zero-day-like attacks.

---

## Project Overview

Traditional intrusion detection systems rely heavily on known attack signatures, which makes them weak against new or unseen threats. This project addresses that limitation by modeling normal network behavior and identifying deviations from it as anomalies.

The system is designed to:
- Learn benign network traffic patterns.
- Detect suspicious traffic using reconstruction error.
- Explain why a traffic window was flagged as anomalous.
- Run in a real-time pipeline for live monitoring.

---

## Key Features

- **Zero-day oriented detection** using anomaly scoring.
- **Attention-based LSTM autoencoder** for sequence learning.
- **Reconstruction error thresholding** for anomaly detection.
- **LLM-based explanation module** for human-readable alerts.
- **Real-time pipeline** with sniffer, Redis, FastAPI, and dashboard.
- **Feature-based analysis** using flow-level network statistics.
- **Dockerized deployment** for consistent setup and portability.

---

## System Architecture

The project follows this pipeline:

1. Network traffic is captured by a sniffer.
2. Flow records are buffered in Redis.
3. FastAPI reads the traffic windows.
4. The model reconstructs the input sequence.
5. Reconstruction error is calculated.
6. If error exceeds the threshold, the traffic is flagged as anomalous.
7. The explanation module generates a readable reason for the alert.
8. Results are displayed on the dashboard.

---

## Dataset

The project uses the **CICIDS2017** dataset, a widely used benchmark for intrusion detection research.

### Why CICIDS2017?
- Contains realistic benign and attack traffic.
- Includes labeled flow-based records.
- Suitable for training anomaly detection models on normal behavior.
- Useful for evaluating zero-day-like detection scenarios.

### Data Usage
- **Training:** benign traffic only.
- **Testing:** benign + attack traffic.
- **Input type:** flow-based features extracted from network traffic.

---

## Selected Features

The model uses important flow-level features such as:

- Flow Duration
- Total Fwd Packets
- Flow Bytes/s
- Flow Packets/s
- Packet Length Mean
- Packet Length Std
- Fwd IAT Mean
- Bwd IAT Mean
- Active Mean
- Idle Mean

These features capture traffic volume, timing, and packet behavior.

---

## Model Description

The core model is an **attention-based LSTM autoencoder**.

### Components
- **Encoder:** LSTM layer that learns temporal patterns.
- **Attention:** Multi-head attention layer that focuses on important time steps.
- **Decoder:** LSTM layer that reconstructs the input sequence.
- **Output layer:** Maps reconstructed hidden states back to the original feature space.

### Detection Logic
The model is trained on normal traffic. During inference, it tries to reconstruct a traffic window. If the reconstruction error is high, the window is considered anomalous.

---

## Why Reconstruction Error?

Reconstruction error measures how different the reconstructed input is from the original input.

- **Low error:** traffic resembles normal behavior.
- **High error:** traffic differs from learned normal patterns.

This makes reconstruction error a natural anomaly score for detecting unknown attacks.

---

## Thresholding Strategy

A threshold is used to convert reconstruction error into a binary decision.

### General approach
- Compute reconstruction errors on validation data.
- Select a high percentile of benign errors as threshold.
- Flag future samples with error above the threshold as anomalous.

This helps control false positives while still detecting abnormal traffic.

---

## Real-Time Pipeline

The system is designed for live traffic monitoring.

### Workflow
- Traffic is captured continuously.
- Redis acts as a fast temporary buffer.
- FastAPI handles inference requests.
- The model scores each traffic window.
- The frontend dashboard displays alerts and explanations.

This makes the project suitable for online intrusion detection rather than offline analysis only.

---

## Results

The model produces clear separation between benign and attack traffic in terms of reconstruction error.

### Observations
- Benign traffic generally has lower reconstruction error.
- Attack traffic produces higher reconstruction error.
- False positive rate is low.
- Detection rate can be improved further.

### Evaluation Metrics
- Detection Rate / Recall
- False Positive Rate
- Confusion Matrix
- Reconstruction Error Distribution
- Mean Error Comparison

---

## Visualizations

The project includes the following analysis plots:

- Error distribution plot
- Mean reconstruction error comparison
- Box plot of errors
- Error over time
- Confusion matrix
- Detection performance bar chart
- Threshold-based anomaly plot
- Feature correlation heatmap

---

## Limitations

- Detection rate is currently modest.
- Some attack traffic overlaps with benign patterns.
- Threshold tuning affects recall and false positives.
- More attack types and better feature engineering can improve performance.

---

## Future Scope

- Improve anomaly detection recall.
- Explore hybrid architectures.
- Add adaptive thresholding.
- Test on additional datasets.
- Improve explanation quality.
- Deploy in a larger real-time network environment.

---

## Tech Stack

- **Python**
- **PyTorch**
- **FastAPI**
- **Redis**
- **Docker**
- **Pandas / NumPy**
- **Scikit-learn**
- **Matplotlib / Seaborn**
- **Frontend dashboard**

---

## Project Structure

```bash
project-root/
├── backend/
├── frontend/
├── models/
├── utils/
├── README.md
└── requirements.txt
```

---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Redis
```bash
docker run -d --name redis -p 6379:6379 redis
```

### 4. Run the backend
```bash
uvicorn backend.main:app --reload
```

### 5. Run the frontend
```bash
npm install
npm run dev
```

### 6. Start the sniffer / data pipeline
```bash
python sniffer.py
```

---

## Conclusion

This project demonstrates a practical approach to zero-day intrusion detection using sequence learning, reconstruction-based anomaly scoring, and real-time alerting. By learning only benign traffic and flagging deviations as suspicious, the system provides a strong foundation for adaptive and explainable network security monitoring.

---

## License

This project is for academic and research purposes.

---

## Author

**Abhiram R S**

---
