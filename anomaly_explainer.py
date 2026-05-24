import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import anthropic
import json

# --- 1. Simulate production spreadsheet data ---
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

# --- 2. Run Isolation Forest ---
features = ["test_voltage", "calibration_offset", "cycle_time_sec", "qc_pass"]
model = IsolationForest(contamination=0.05, random_state=42)
df["anomaly"] = model.fit_predict(df[features])

flagged = df[df["anomaly"] == -1].copy()
print(f"Flagged {len(flagged)} rows for review:\n{flagged.to_string()}\n")

# --- 3. Build prompt with flagged data as context ---
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

# --- 4. Send to Claude, print response ---
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)

print("=== Claude's Analysis ===")
print(message.content[0].text)