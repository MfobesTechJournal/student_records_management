def validate_non_empty(value, field):
    if not value.strip():
        raise ValueError(f"{field} cannot be empty")
    return value.strip()
