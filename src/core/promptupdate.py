from core.helper import Helper

def deep_merge(oldconfig: dict, newpayload: dict):
    for key, value in newpayload.items():
        if isinstance(value, dict) and key in oldconfig and isinstance(oldconfig[key], dict):
            deep_merge(oldconfig[key], value)
        else:
            oldconfig[key] = value
    return oldconfig

def update_prompt(payload):
    config_path = "src/config/prompt.yaml"
    config      = Helper.load_yaml(config_path)
    updated     = deep_merge(config,payload)
    updated     = Helper.deep_literal_transform(updated)
    Helper.save_yaml(updated, config_path)
    return updated
