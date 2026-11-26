"""Baryta's names over NegPy's: the strings and guides keep NegPy's text, so upstream merges stay clean."""

import json
import re
from pathlib import Path
from typing import NamedTuple

APP_NAME = "Baryta"
UPSTREAM_NAME = "NegPy"
UPSTREAM_REPO = "marcinz606/NegPy"
NAMES_CATALOG = "negpy/translations/baryta_names.json"
# Languages that join a word to the next one (no spaces, or Korean particles), so a name has no word edge.
_JOINED = ("ja", "ko", "zh_CN")


class _Name(NamedTuple):
    in_source: re.Pattern
    plain: str
    local: list[tuple[re.Pattern, str]]
    local_plain: str


_names: list[_Name] = []


def _word(term: str, edges: bool = True) -> re.Pattern:
    return re.compile(rf"(?<!\w){re.escape(term)}(?!\w)" if edges else re.escape(term))


def use_plain_names(language: str) -> None:
    """Show Baryta's plain control names in place of NegPy's darkroom names. Off until the app starts,
    so NegPy's own tests read NegPy's names."""
    from negpy.kernel.system.paths import get_resource_path

    def read(path: str) -> dict:
        return json.loads(Path(get_resource_path(path)).read_text(encoding="utf-8"))

    table = read(NAMES_CATALOG)
    local = table.get(language, {}) if language != "en" else {}
    catalog = read(f"negpy/translations/{language}.json") if local else {}
    edges = language not in _JOINED
    _names.clear()
    for term, plain in sorted(table["en"].items(), key=lambda item: len(item[0]), reverse=True):
        # A plain name, or {phrase: plain phrase} where an article changes with it ("la Filtratura").
        forms = local.get(term, {})
        forms = {catalog[term]: forms} if isinstance(forms, str) and term in catalog else forms if isinstance(forms, dict) else {}
        ordered = sorted(forms.items(), key=lambda item: len(item[0]), reverse=True)
        _names.append(_Name(_word(term), plain, [(_word(a, edges), b) for a, b in ordered], forms.get(catalog.get(term, ""), "")))


def stop_plain_names() -> None:
    _names.clear()


def brand(text: str, source: str | None = None) -> str:
    """The app's name in place of the upstream one, in display text only (never in values, paths or keys).
    source is the English text that text translates: a name changes only where the source holds it, since
    one translated word can stand for two English names (Finish and Finishing)."""
    translated = source is not None and text != source
    text = text.replace(UPSTREAM_NAME, APP_NAME)
    source = text if source is None else source
    for name in _names:
        if name.in_source.search(source):
            for pattern, plain in name.local:
                text = pattern.sub(plain, text)
            # A translation can keep the English name (Lab, CLAHE).
            text = name.in_source.sub(name.local_plain if translated and name.local_plain else name.plain, text)
    return text
