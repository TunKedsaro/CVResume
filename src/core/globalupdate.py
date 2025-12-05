from core.helper import Helper

def deep_merge(old: dict, new: dict):
    for key, value in new.items():
        if isinstance(value, dict) and key in old and isinstance(old[key], dict):
            deep_merge(old[key], value)
        else:
            old[key] = value
    return old

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


