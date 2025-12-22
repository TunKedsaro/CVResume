from core.helper import Helper

def deep_merge(old: dict, new: dict):
    """
    Recursively merge values from `new` into `old`.
    - Nested dictionaries are merged deeply.
    - Non-dict values overwrite existing values.
    Args:
        old (dict): Base dictionary to be updated.
        new (dict): New values to merge into the base.
    Returns:
        dict: The updated dictionary.
    """
    for key, value in new.items():
        if isinstance(value, dict) and key in old and isinstance(old[key], dict):
            deep_merge(old[key], value)
        else:
            old[key] = value
    return old

### global.yaml #############################################################
def update_global(payload: dict):
    """
    Update `global.yaml` configuration using a partial payload.
    - Loads existing global configuration
    - Merges provided fields into the config
    - Ignores None values
    - Saves the updated configuration back to disk
    Args:
        payload (dict): Partial configuration values to update.
    Returns:
        dict: Updated global configuration.
    """
    config_path = "src/config/global.yaml"
    config = Helper.load_yaml(config_path)
    clean_payload = {k: v for k, v in payload.items() if v is not None}
    updated = deep_merge(config, clean_payload)
    print(updated)
    Helper.save_yaml(updated,config_path)
    return updated
# p0 = {
#     "version": "global_v1"
# }
# p1 = {
#     "version": "global_v2",
#     "scoring": {
#         "final_score_max": 120,
#         "round_digits": 1
#     }
# }
# p2 = {
#     "version":"global_v3",
#     "scoring":{
#         "final_score_max":100
#     }
# }
# update_global(p1)

#############################################################################
#############################################################################

### model.yaml ##############################################################

def update_model(payload: dict):
    """
    Update `model.yaml` configuration using a partial payload.
    Typically used to change model provider or generation model
    without overwriting unrelated configuration fields.
    Args:
        payload (dict): Partial model configuration values.
    Returns:
        dict: Updated model configuration.
    """
    config_path = "src/config/model.yaml"
    config = Helper.load_yaml(config_path)
    clean_payload = {k: v for k, v in payload.items() if v is not None}
    updated = deep_merge(config, clean_payload)
    print(updated)
    Helper.save_yaml(updated,config_path)
    return updated

# pl0 = {
#     "provider":"google",
#     "generation_model":"gemini-2.5-flash"
# }
# pl1 = {
#     "provider":"OpenAI",
#     "generation_model":"gpt5"
# }
# update_model(pl0)

#############################################################################
#############################################################################

### weight.yaml ##############################################################
def update_weight(payload: dict):
    """
    Update `weight.yaml` configuration using a partial payload.
    Used to modify section weights, criteria weights,
    or version metadata without replacing the full config.
    Args:
        payload (dict): Partial weight configuration values.
    Returns:
        dict: Updated weight configuration.
    """
    config_path = "src/config/weight.yaml"
    config = Helper.load_yaml(config_path)
    clean_payload = {k: v for k, v in payload.items() if v is not None}
    updated = deep_merge(config, clean_payload)
    print(updated)
    Helper.save_yaml(updated,config_path)
    return updated

# p1 = {
#         "version":"weights_v3",
#         "weights":{
#             "Profile":{
#                 "section_weight":0.2
#             }
#         }
#     }

# update_weight(p1)

##############################################################################
##############################################################################

### Prompt.yaml ##############################################################
def update_prompt(payload):
    """
    Update `prompt.yaml` configuration.
    - Merges new prompt content into existing configuration
    - Applies literal formatting transformation
    - Saves updated prompt configuration
    Args:
        payload (dict): Prompt configuration updates.
    Returns:
        dict: Updated prompt configuration.
    """
    config_path = "src/config/prompt.yaml"
    config      = Helper.load_yaml(config_path)
    updated     = deep_merge(config,payload)
    updated     = Helper.deep_literal_transform(updated)
    Helper.save_yaml(updated, config_path)
    return updated

##############################################################################
##############################################################################