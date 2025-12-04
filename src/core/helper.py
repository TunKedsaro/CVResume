import yaml
import json
import os

class Helper:
    @staticmethod
    def load_file(filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def load_yaml(filepath: str) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def fop(num: float) -> float:
        return float(f"{num:.1f}")

    @staticmethod
    def jsonstr(obj) -> str:
        return json.dumps(obj, indent=4, ensure_ascii=False)