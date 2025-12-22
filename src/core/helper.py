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
    """
    Utility helper class for file I/O, YAML/JSON handling,
    formatting, and configuration transformations.
    """
    @staticmethod
    def load_file(filepath: str) -> str:
        """
        Load and return the contents of a text file.
        Args:
            filepath (str): Path to the file.
        Returns:
            str: File contents.
        """
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
        
    @staticmethod
    def load_yaml(filepath: str) -> dict:
        """
        Load a YAML file and return its contents as a dictionary.
        Args:
            filepath (str): Path to the YAML file.
        Returns:
            dict: Parsed YAML content.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
        
    @staticmethod
    def load_json(filepath: str) -> dict:
        """
        Load a JSON file and return its contents as a dictionary.
        Args:
            filepath (str): Path to the JSON file.
        Returns:
            dict: Parsed JSON content.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
        
    @staticmethod
    def save_yaml(newconfig,filepath: str):
        """
        Save a dictionary to a YAML file.
        Preserves key order and applies custom representers
        such as block literal formatting.
        Args:
            newconfig (dict): Configuration data to save.
            filepath (str): Output YAML file path.
        """
        with open(filepath,"w",encoding="utf-8") as file:
            return yaml.dump(newconfig,file,sort_keys=False)
        
    @staticmethod
    def fop(num: float) -> float:
        """
        Format a number to one decimal place.
        Args:
            num (float): Input number.
        Returns:
            float: Rounded number with one decimal precision.
        """
        return float(f"{num:.1f}")
    
    @staticmethod
    def prettyjson(txt:str) -> str:
        """
        Pretty-print a JSON-compatible object as a formatted string.
        Args:
            txt (str): JSON-compatible object.
        Returns:
            str: Indented JSON string.
        """
        return str(json.dumps(txt,indent=4, ensure_ascii=False))
    
    @staticmethod
    def to_literal(value):
        """
        Convert multiline strings into LiteralString for YAML output.
        Single-line strings and non-string values are returned unchanged.
        """
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