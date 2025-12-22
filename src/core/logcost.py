from core.helper import Helper

ip_token_price = Helper.load_yaml("src/config/global.yaml")['pricing']['gemini_2_5_flash']['input_per_million']
op_token_price = Helper.load_yaml("src/config/global.yaml")['pricing']['gemini_2_5_flash']['output_per_million']

def estimate_gemini_cost(api_response):
    """
    Estimate token usage cost for a Gemini API response.
    Calculates input and output token costs based on pricing
    defined in `global.yaml` and usage metadata returned by
    the Gemini API.
    Args:
        api_response:
            Raw response object returned by the Gemini client,
            expected to contain `usage_metadata`.
    Returns:
        dict:
            {
                "prompt_tokens": int,
                "output_tokens": int,
                "input_cost": float,
                "output_cost": float,
                "total_cost": float
            }
    """
    print(f"src/core/geminicost->def estimate_gimini_cost ...")
    # Pricing
    # source : https://ai.google.dev/gemini-api/docs/pricing

    input_cost_per_m  = ip_token_price    # Gemini 2.5 Flash Input  tokens cost $0.30 per 1 million tokens
    output_cost_per_m = op_token_price    # Gemini 2.5 Flash Output tokens cost $2.52 per 1 million tokens

    tokens        = api_response.usage_metadata
    prompt_tokens = tokens.prompt_token_count
    output_tokens = tokens.candidates_token_count

    input_cost    = (prompt_tokens/1000000) * input_cost_per_m
    output_cost   = (output_tokens/1000000) * output_cost_per_m
    
    return {
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(input_cost + output_cost, 6),
    }

    # print(returnx)

# caller = LlmCaller()
# agg = SectionScoreAggregator()

# caller = LlmCaller()
# parsed, raw_resp = caller.call(
#     "Return this as JSON: {'status':'connected'}"
# )
# print(parsed)
# estimate_gemini_cost(raw_resp)