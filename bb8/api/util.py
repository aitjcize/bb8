def validate_uint(val, min_val, max_val, default_val):
    try:
        val = int(val)
    except ValueError:
        return default_val
    if (min_val >= 0 and val < min_val) or \
       (max_val >= 0 and val > max_val):
        return default_val
    return val
