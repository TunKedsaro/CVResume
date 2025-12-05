import yaml
import json
import os

class Helper:
    @staticmethod
    def load_file(filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def load_yaml(filepath: str) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
        
    @staticmethod
    def save_yaml(newconfig,filepath: str):
        with open(filepath,"w",encoding="utf-8") as file:
            return yaml.dump(newconfig,file,sort_keys=False)

    @staticmethod
    def fop(num: float) -> float:
        return float(f"{num:.1f}")

    @staticmethod
    def jsonstr(obj) -> str:
        return json.dumps(obj, indent=4, ensure_ascii=False)
    
    @staticmethod
    def prettyjson(txt:str) -> str:
        return str(json.dumps(txt,indent=4, ensure_ascii=False))