"""Baryta's grouping of the per-frame cards into Frame tabs.

The cards stay NegPy's own; only this table says which tab holds which card, so an upstream merge
touches one place. A tab key keeps its upstream name where the tab keeps its job, because shortcuts
and the saved tab resolve by key.
"""

from negpy.kernel.system.i18n import tr


def frame_tabs() -> list[tuple[str, str, list[str]]]:
    """(key, title, card section attributes on ControlsPanel), in tab order."""
    return [
        ("geometry", tr("Geometry"), ["autocrop_section", "geometry_section"]),
        ("color", tr("Color"), ["color_section"]),
        ("tone", tr("Tone"), ["tone_section", "paper_section"]),
        ("finish", tr("Finish"), ["lab_section", "toning_section", "finish_section", "altproc_section"]),
        ("retouch", tr("Retouch"), ["retouch_section", "local_section"]),
    ]
