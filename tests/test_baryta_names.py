import json
import re
from collections.abc import Callable, Iterator

import pytest

from negpy.kernel.system import brand
from negpy.kernel.system.i18n import configure, tr
from scripts.extract_translations import CATALOGS, ENGLISH_GUIDE, TRANSLATIONS, extract

NAMES = json.loads((TRANSLATIONS / "baryta_names.json").read_text(encoding="utf-8"))


def _word(term: str) -> re.Pattern:
    return re.compile(rf"(?<!\w){re.escape(term)}(?!\w)")


@pytest.fixture
def plain() -> Iterator[Callable[[str], None]]:
    yield lambda language: brand.use_plain_names(configure(language))
    brand.stop_plain_names()
    configure("en")


def test_names_stay_off_until_the_app_turns_them_on() -> None:
    assert tr("Print Density") == "Print Density"


def test_a_plain_name_replaces_whole_names_only(plain) -> None:
    plain("en")
    assert tr("Print Density") == "Brightness"
    assert tr("Shadows Grade Trim") == "Shadows Contrast Trim"
    assert tr("Auto Density and Grade") == "Auto Brightness and Contrast"
    assert brand.brand("Label and Labrador") == "Label and Labrador"


def test_a_translated_word_changes_only_where_the_english_names_it(plain) -> None:
    plain("ja")
    # One Japanese word stands for both the Finish tab and the Finishing card.
    assert tr("Finish") == "仕上げ"
    assert tr("Finishing") == NAMES["ja"]["Finishing"]
    # A translation that keeps the English name takes the local plain name.
    assert tr("CLAHE") == NAMES["ja"]["CLAHE"]


def test_an_article_changes_with_its_name(plain) -> None:
    plain("it")
    assert tr("ISO-R Grade") == "Contrasto"
    assert "il Contrasto" in brand.brand("imposta anche la Gradazione ISO-R", "also sets ISO-R Grade")


def test_every_name_still_names_a_negpy_string() -> None:
    """An upstream rename leaves a name with nothing to replace."""
    texts = [*extract(), ENGLISH_GUIDE.read_text(encoding="utf-8")]
    for term in NAMES["en"]:
        assert any(_word(term).search(text) for text in texts), f"{term!r} names no NegPy string"


@pytest.mark.parametrize("locale", sorted(CATALOGS))
def test_every_local_name_matches_its_catalog(locale: str) -> None:
    catalog = json.loads(CATALOGS[locale].read_text(encoding="utf-8"))
    guide_path = TRANSLATIONS / f"USER_GUIDE.{locale}.md"
    guide = guide_path.read_text(encoding="utf-8") if guide_path.exists() else ""
    texts = "\n".join([*catalog.values(), guide])
    for term, plain in NAMES.get(locale, {}).items():
        assert term in NAMES["en"], f"{locale}: {term!r} has no English name"
        forms = {catalog.get(term, ""): plain} if isinstance(plain, str) else plain
        for phrase in forms:
            assert phrase and phrase in texts, f"{locale}: {term!r} no longer reads {phrase!r} in the catalog"
