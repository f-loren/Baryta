"""Baryta's top bar: the three phases of the work, the open file, and the frame's Reset and Export.

Every control drives a part of NegPy that already exists; the bar holds no state of its own.
"""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from negpy.desktop.view.styles.templates import TOP_ROW_HEIGHT, labeled_action
from negpy.desktop.view.styles.theme import THEME
from negpy.desktop.view.widgets.elided_label import ElidedLabel
from negpy.desktop.view.widgets.segmented_choice import SegmentedChoice
from negpy.kernel.system.i18n import tr

# Right panel group -> phase. Groups that belong to no phase (Metadata, Export) leave the choice as it is.
_PHASE_OF_GROUP = {"scan": "scan", "library": "library", "roll": "frame", "frame": "frame"}


class BarytaTopBar(QWidget):
    def __init__(self, window) -> None:
        super().__init__()
        self._window = window
        controller = window.controller
        right = window.right_panel
        self.setFixedHeight(TOP_ROW_HEIGHT)

        self.phase = SegmentedChoice(
            (("fa5s.camera", tr("Scan")), ("mdi6.bookshelf", tr("Library")), ("fa5s.sliders-h", tr("Develop"))),
            tr("Scan film, pick a roll, or edit the open frame"),
            data=("scan", "library", "frame"),
        )
        self.phase.currentChanged.connect(lambda _i: right.show_tab_by_key(self.phase.currentData()))
        right.group_stack.currentChanged.connect(self._follow_panel)
        self._follow_panel(right.group_stack.currentIndex())

        self.file_label = ElidedLabel("")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setToolTip(tr("The open frame"))
        controller.image_updated.connect(self._show_file)

        self.reset_btn = labeled_action("fa5s.history", tr("Reset"), tr("Discard all edits and return this frame to its default look"))
        self.reset_btn.clicked.connect(controller.session.reset_settings)
        self.export_btn = labeled_action(
            "fa5s.file-export", tr("Export"), tr("Export this frame with the settings on the Export tab"), primary=True
        )
        self.export_btn.clicked.connect(controller.request_export)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, THEME.space_sm)
        row.setSpacing(THEME.space_sm)
        row.addWidget(self.phase)
        row.addWidget(self.file_label, 1)
        row.addWidget(self.reset_btn)
        row.addWidget(self.export_btn)

    def _follow_panel(self, index: int) -> None:
        keys = self._window.right_panel._group_keys
        phase = _PHASE_OF_GROUP.get(keys[index]) if 0 <= index < len(keys) else None
        if phase is not None:
            self.phase.blockSignals(True)
            self.phase.setCurrentIndex(self.phase.findData(phase))
            self.phase.blockSignals(False)

    def _show_file(self) -> None:
        path = self._window.controller.state.current_file_path
        self.file_label.setText(os.path.basename(path) if path else "")
