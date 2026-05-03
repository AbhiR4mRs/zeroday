from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = BASE_DIR / "raw" / "MachineLearningCVE"
PROCESSED_DATA_DIR = BASE_DIR / "processed"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Files
BENIGN_FILES = [
    "Monday-WorkingHours.pcap_ISCX.csv",
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv",
    "Friday-WorkingHours-Morning.pcap_ISCX.csv"
]

ATTACK_FILES = [
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv"
]

# Features
FEATURES = [
    "Flow Duration",
    "Total Fwd Packets",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Packet Length Mean",
    "Packet Length Std",
    "Fwd IAT Mean",
    "Bwd IAT Mean",
    "Active Mean",
    "Idle Mean"
]

WINDOW_SIZE = 10
