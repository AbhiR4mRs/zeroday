# # src/llm_analysis/prompt_builder.py
# def build_prompt(deviation_dict):
#     # Filter to significant deviations
#     significant = {
#         k: v for k, v in deviation_dict.items()
#         if abs(v) > 0.5
#     }

#     if not significant:
#         # Fallback if nothing stands out numerically
#         summary = "No single feature shows a very large deviation, but the overall pattern differs from normal benign traffic."
#     else:
#         summary_lines = []
#         for feat, val in significant.items():
#             direction = "higher" if val > 0 else "lower"
#             summary_lines.append(f"- {feat}: {direction} than normal (deviation {val:.2f})")
#         summary = "\n".join(summary_lines)

#     prompt = (
#         "You are an intrusion detection analysis assistant.\n"
#         "A network traffic window has been flagged as anomalous by an autoencoder-based IDS.\n"
#         "Your ONLY job is to explain WHY this window looks suspicious based on the feature deviations.\n"
#         "Do NOT recommend using any other intrusion detection systems or security tools.\n"
#         "Do NOT give generic advice like 'use an IDS' or 'monitor the system'.\n"
#         "Focus only on describing what is unusual about this traffic.\n\n"
#         "Here are the feature deviations compared to normal benign traffic:\n"
#         f"{summary}\n\n"
#         "Explain in 3–5 sentences:\n"
#         "- Which features look abnormal.\n"
#         "- What kind of abnormal behavior this suggests (for example: DoS-like activity, scanning, or data exfiltration).\n"
#         "- Why these deviations are enough for the system to flag this window as suspicious.\n"
#     )

#     return prompt


def build_prompt(deviation_dict):
    significant = {
        k: v for k, v in deviation_dict.items()
        if abs(v) > 0.5   # deviation threshold (tunable)
    }

    prompt = (
        "You are a cybersecurity analyst assistant.\n"
        "The following network traffic window was detected as anomalous.\n\n"
        "Observed feature deviations:\n"
    )

    for feat, val in significant.items():
        prompt += f"- {feat}: deviation {val:.2f}\n"

    prompt += (
        "\nTasks:\n"
        "1. Explain why this traffic may be anomalous.\n"
        "2. Suggest the most likely type of cyber attack.\n"
        "3. Recommend mitigation steps.\n"
    )

    return prompt