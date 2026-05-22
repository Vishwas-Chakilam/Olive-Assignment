def normalize_model_name(model: str) -> str:
    """Normalize UI input like 'gemini-2.5 flash' -> 'gemini-2.5-flash'."""
    normalized = model.strip().lower().replace(" ", "-")
    aliases = {
        "gemini-2.5-flash": "gemini-2.5-flash",
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-1.5-flash": "gemini-1.5-flash",
    }
    return aliases.get(normalized, normalized)
