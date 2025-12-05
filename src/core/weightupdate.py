from core.helper import Helper

def deep_merge(oldconfig:dict,newpayload:dict):
    for key,value in newpayload.items():
        print(f"key -> {key} ,value -> {value}")
        if isinstance(value,dict) and key in oldconfig and isinstance(oldconfig[key],dict):
            deep_merge(oldconfig[key],value)
        else:
            oldconfig[key] = value
    return oldconfig


def update_weight(payload):
    config_path = "src/config/weight.yaml"
    config      = Helper.load_yaml(config_path)
    updated = deep_merge(
        oldconfig  = config,
        newpayload = payload
    )
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



# # from core.helper import Helper

# # def deep_merge(old: dict, new: dict):
# #     for key, value in new.items():
# #         if isinstance(value, dict) and key in old and isinstance(old[key], dict):
# #             deep_merge(old[key], value)
# #         else:
# #             old[key] = value
# #     return old

# # def update_global(payload: dict):
# #     config_path = "src/config/global.yaml"
# #     config = Helper.load_yaml(config_path)
# #     clean_payload = {k: v for k, v in payload.items() if v is not None}
# #     updated = deep_merge(config, clean_payload)
# #     print(updated)
# #     Helper.save_yaml(updated,config_path)
# #     return updated
