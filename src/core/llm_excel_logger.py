import pandas as pd
from pathlib import Path
from datetime import datetime, timezone, timedelta
import yaml
def load_yaml(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
        
LOG_FILE = Path("logs/gemini_usage.csv")

COLUMNS = [
    "timestamp",
    "id",
    "Model",
    "output_lange",
    "prompt_length_chars",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "input_cost",
    "output_cost",
    "estimated_cost_usd",
    "estimated_cost_thd",
    "response_time_sec"
]

def log_llm_usage(row: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    row["timestamp"] = datetime.now(
        tz=timezone(timedelta(hours=7))
    ).isoformat()
    row["Model"] = load_yaml("src/config/model.yaml")['model']['generation_model']

    if LOG_FILE.exists():
        df = pd.read_csv(LOG_FILE)
    else:
        df = pd.DataFrame(columns=COLUMNS)

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)
