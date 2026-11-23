"""Baryta's name over NegPy's: the strings and guides keep NegPy's text, so upstream merges stay clean."""

APP_NAME = "Baryta"
UPSTREAM_NAME = "NegPy"
UPSTREAM_REPO = "marcinz606/NegPy"


def brand(text: str) -> str:
    """The app's name in place of the upstream one, in display text only (never in values, paths or keys)."""
    return text.replace(UPSTREAM_NAME, APP_NAME)
