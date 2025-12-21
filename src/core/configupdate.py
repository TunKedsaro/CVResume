from core.helper import Helper

def deep_merge(old: dict, new: dict):
    for key, value in new.items():
        if isinstance(value, dict) and key in old and isinstance(old[key], dict):
            deep_merge(old[key], value)
        else:
            old[key] = value
    return old

### global.yaml #############################################################
def update_global(payload: dict):
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
    config_path = "src/config/prompt.yaml"
    config      = Helper.load_yaml(config_path)
    updated     = deep_merge(config,payload)
    updated     = Helper.deep_literal_transform(updated)
    Helper.save_yaml(updated, config_path)
    return updated

##############################################################################
##############################################################################