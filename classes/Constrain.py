# arduino style helper function
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))