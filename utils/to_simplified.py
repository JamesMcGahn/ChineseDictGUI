def to_simplified(text: str) -> str:
    try:
        if not text:
            return ""
        from opencc import OpenCC

        return OpenCC("t2s").convert(text)  # Traditional → Simplified
    except Exception:
        return text
