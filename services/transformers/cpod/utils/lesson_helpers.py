import re
from urllib.parse import urlparse


def extract_slug(input_str: str) -> str | None:
    """
    Extracts the slug from a lesson URL or returns the input
    if it's already a slug.

    Supports:
    - https://www.xyz.com/lesson/personal-finances
    - https://www.xyz.com/lessons/personal-finances#dialogue
    - personal-finances
    """

    input_str = re.sub(r"[.,;:!?)]*$", "", input_str)

    # If it's a full URL, parse the path
    if input_str.startswith("http"):
        path = urlparse(input_str).path  # e.g., "/lesson/personal-finances"
        match = re.search(r"/lessons?/([^/?#]+)", path)
        return match.group(1) if match else None

    # If it's already a slug (e.g., "personal-finances")
    if re.fullmatch(r"[a-z0-9\-]+", input_str):
        return input_str

    return None


def extract_hash(url: str) -> str | None:
    if not url:
        return None
    parts = url.split("/")
    if len(parts) > 4:
        return parts[4]
    return None
