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
