from core.helper import Helper
def update_model(payload):
    config_file  = Helper.load_yaml("src/config/model.yaml")
    config_value = config_file["model"]
    keypayload   = [i for i,_ in payload.items()]
    newconfig    = dict()
    for key,value in config_value.items():
        if key in keypayload:
            newconfig[key] = payload[key]
        else:
            newconfig[key] = value
    # print(f"before -> {config_file}")
    config_file["model"] = newconfig
    # print(f"after  -> {config_file}")
    
    # with open("src/config/model.yaml","w",encoding="utf-8") as f:
    #     return yaml.dump(config_file,f,sort_keys=False)

    Helper.save_yaml(config_file,"src/config/model.yaml")

# pl0 = {
#     "provider":"google",
#     "generation_model":"gemini-2.5-flash"
# }
# pl1 = {
#     "provider":"OpenAI",
#     "generation_model":"gpt5"
# }
# update_model(pl0)