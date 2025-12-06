import yaml
import json
import os

class LiteralString(str):
    """Force YAML to use block literal style '|'."""
    pass
def literal_representer(dumper,value):
    """Represent LiteralString using YAML block style."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', value, style='|')

# Register custom representer
yaml.add_representer(LiteralString, literal_representer)

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
    def load_json(filepath: str) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
        
    @staticmethod
    def save_yaml(newconfig,filepath: str):
        with open(filepath,"w",encoding="utf-8") as file:
            return yaml.dump(newconfig,file,sort_keys=False)
        
    @staticmethod
    def fop(num: float) -> float:
        return float(f"{num:.1f}")
    
    @staticmethod
    def prettyjson(txt:str) -> str:
        return str(json.dumps(txt,indent=4, ensure_ascii=False))
    
    @staticmethod
    def to_literal(value):
        """Convert multiline strings to LiteralString (YAML writes as block '|')"""
        if isinstance(value,str) and "\n" in value:
            return LiteralString(value)
        return value
    
    @staticmethod
    def deep_literal_transform(data):
        '''
        Recursively convert ALL multiline strings inside dict/list
        into LiteralString so block formatting is preserved
        '''
        if isinstance(data, dict):
            return {k: Helper.deep_literal_transform(v) for k,v in data.items()}
        if isinstance(data, list):
            return [Helper.deep_literal_transform(i) for i in data]
        # Convert only multiline string
        return Helper.to_literal(data)