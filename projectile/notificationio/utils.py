def changed_fields_with_values(key, previous_data, current_data):
    return {key: {"saved": previous_data, "current": current_data}}
