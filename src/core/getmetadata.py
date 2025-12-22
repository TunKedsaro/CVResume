from core.helper import Helper
import os 
from datetime import datetime,timezone,timedelta

def get_metadata():
    """
    Collect runtime, configuration, and system metadata for the service.
    Loads current configuration files (global, model, prompt, weights)
    and returns a consolidated metadata object used for health checks,
    debugging, and service introspection.
    Includes:
    - Configuration versions and summaries
    - Model and prompt metadata
    - Section weight information
    - System environment details and timestamp
    Returns:
        dict: Service metadata snapshot.
    """
    global_cfg  = Helper.load_yaml("src/config/global.yaml")
    model_cfg   = Helper.load_yaml("src/config/model.yaml")
    prompt_cfg  = Helper.load_yaml("src/config/prompt.yaml")
    weight_cfg  = Helper.load_yaml("src/config/weight.yaml")

    metadata = {
        "global": {
            "version": global_cfg.get("version"),
            "GOOGLE_API_KEY_set": os.getenv("GOOGLE_API_KEY") is not None
        },
        "model": model_cfg.get("model"),
        "prompt_metadata": {
            "version": prompt_cfg.get("version"),
            "roles_count": len(prompt_cfg.get("role", {})),
            "sections_supported": list(prompt_cfg.get("expected_content", {}).keys()),
            "output_formats": list(prompt_cfg.get("output", {}).keys())
        },
        "weights_metadata": {
            "version": weight_cfg.get("version"),
            "sections": list(weight_cfg.get("weights", {}).keys()),
            "section_weights": {
                sec: weight_cfg["weights"][sec]["section_weight"]
                for sec in weight_cfg["weights"]
            }
        },
        "system": {
            "timestamp": str(datetime.now(tz=(timezone(timedelta(hours=7))))),
            "environment": "docker/dev",
            "python_version": "3.12",
            "service_version": "0.1.4"
        }
    }

    return metadata
