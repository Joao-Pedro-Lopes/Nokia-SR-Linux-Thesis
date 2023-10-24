def transform_dict(input_dict):
    output_dict = {}
    for key, value in input_dict.items():
        transformed_keys = []
        for inner_key in value.keys():
            if inner_key.startswith("e"):
                transformed_key = inner_key.replace("e", "ethernet-", 1)
            else:
                transformed_key = inner_key
            transformed_keys.append(transformed_key)
        output_dict[key] = transformed_keys
    return output_dict