"""Slug generation utilities for nes2."""

import re
import unicodedata


def text_to_slug(text: str) -> str:
    """Convert text to a URL-friendly slug.

    Args:
        text: Input text to convert to slug

    Returns:
        Lowercase slug with hyphens, containing only alphanumeric characters and dashes
    """
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Convert to lowercase
    text = text.lower()

    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)

    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^a-z0-9-]", "", text)

    # Remove multiple consecutive hyphens
    text = re.sub(r"-+", "-", text)

    # Strip leading/trailing hyphens
    text = text.strip("-")

    return text
