import json
from pathlib import Path

import anthropic
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import IsolationForest

load_dotenv(Path(__file__).resolve().parent / ".env")

# --- Step 0.1: Setup - Simulate production spreadsheet data ---
# unit_id | test_voltage | calibration_offset | cycle_time_sec | qc_pass
# UNIT-000 |    12.05     |       0.51         |      44.3      |    1
# UNIT-001 |    11.89     |       0.48         |      47.1      |    0

np.random.seed(42)
n = 50

df = pd.DataFrame({
    "unit_id": [f"UNIT-{i:03d}" for i in range(n)],
    "test_voltage": np.random.normal(12.0, 0.2, n),
    "calibration_offset": np.random.normal(0.5, 0.05, n),
    "cycle_time_sec": np.random.normal(45, 3, n),
    "qc_pass": np.random.choice([1, 1, 1, 0], n),  # mostly passing
})

# Inject obvious anomalies
df.loc[5, "test_voltage"] = 18.7       # way too high
df.loc[12, "cycle_time_sec"] = 120     # 2x normal cycle time
df.loc[23, "calibration_offset"] = -1.2  # negative and far off

# --- Step 0.2. Run Isolation Forest ---
features = ["test_voltage", "calibration_offset", "cycle_time_sec", "qc_pass"]
model = IsolationForest(contamination=0.05, random_state=42)
df["anomaly"] = model.fit_predict(df[features])

flagged = df[df["anomaly"] == -1].copy()
print(f"Flagged {len(flagged)} rows for review:\n{flagged.to_string()}\n")

# --- Step 1. Build prompt with flagged data as context ---
column_context = """
Column definitions:
- test_voltage: expected range 11.5–12.5V
- calibration_offset: expected range 0.4–0.6
- cycle_time_sec: expected range 38–52 seconds
- qc_pass: 1 = passed QC, 0 = failed
"""

flagged_json = flagged[["unit_id"] + features].to_dict(orient="records")

prompt = f"""
You are a manufacturing operations assistant reviewing thermal camera production data.

{column_context}

The following units were flagged as anomalies by an automated detection system.
For each unit, explain what looks wrong based on the column definitions, 
and suggest a concrete next step for the operations team.

Flagged units:
{json.dumps(flagged_json, indent=2)}

Respond in plain language. Be specific about which values are out of range.
"""

# --- Step 2: Model Execution ---
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)

# --- Step 3 & 4: Response and Next Step ---
print("=== Claude's Analysis ===")
print(message.content[0].text)