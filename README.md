# Anomaly Explainer

A small demo that flags unusual rows in simulated manufacturing data, then asks Claude to explain what looks wrong and what to do next.

## First-time setup

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Check that it worked:

```bash
uv --version
```

You should see a version number, not "command not found".

### 2. Add your API key

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your real key from [console.anthropic.com](https://console.anthropic.com/):

## How to run

From root:

```bash
uv sync
uv run anomaly_explainer.py
```

## Sample Prompt Output 

```
# Anomaly Analysis Report

## UNIT-005
**What's wrong:** The test voltage is significantly out of range at **18.7V** (expected 11.5–12.5V). This is approximately 50% higher than the upper limit. All other parameters (calibration offset and cycle time) are within normal ranges.

**Suggested next step:** Investigate the power supply or voltage regulator feeding this test station. This could indicate a faulty power supply unit, a damaged voltage regulator, or a wiring issue. Quarantine this unit and inspect for component damage from overvoltage before any rework attempt.

---

## UNIT-012
**What's wrong:** The cycle time is drastically out of range at **120.0 seconds** (expected 38–52 seconds). This is more than double the maximum expected time. Voltage and calibration offset are both within acceptable ranges.

**Suggested next step:** Review the production log for this unit to identify where the process stalled or slowed down. This could indicate a station malfunction, a mechanical jam, or an operator intervention. Check if the test equipment timed out or if there was a process interruption that needs to be addressed systemically.

---

## UNIT-023
**What's wrong:** The calibration offset is severely out of range at **-1.2** (expected 0.4–0.6). This is a negative value when only positive values in a narrow band are expected. **Critically, this unit passed QC (qc_pass = 1) despite this major deviation.**

**Suggested next step:** This is the most concerning unit—it indicates a potential gap in the QC inspection criteria. Immediately recall or hold this unit before shipment. Audit the QC checkpoint to determine why a negative calibration offset didn't trigger a failure. The QC pass logic or sensor calibration verification step may need to be corrected to catch this type of defect.
```
