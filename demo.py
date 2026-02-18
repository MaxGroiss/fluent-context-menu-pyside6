"""Interactive demo for FluentContextMenu.

Run directly::

    python demo.py

Right-click the text editor or the coloured panel to see the context menu.
Toggle the *Dark Mode* checkbox to switch themes on the fly.
The status bar demonstrates all three return-value patterns (callback,
signal, item-def reference).
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from fluent_context_menu import (
    DARK,
    LIGHT,
    FluentContextMenu,
    MenuItemDef,
    _Theme,
    svg_to_icon,
)


# ---------------------------------------------------------------------------
# Inline SVG icons (Lucide-style, stroke="currentColor")
# ---------------------------------------------------------------------------

_SVG_CUT = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" y1="4" x2="8.12" y2="15.88"/><line x1="14.47" y1="14.48" x2="20" y2="20"/><line x1="8.12" y1="8.12" x2="12" y2="12"/></svg>'
_SVG_COPY = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
_SVG_PASTE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>'
_SVG_SELECT = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 12l2 2 4-4"/></svg>'
_SVG_UNDO = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>'
_SVG_REDO = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>'
_SVG_BOLD = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg>'
_SVG_ITALIC = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>'
_SVG_UNDERLINE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3"/><line x1="4" y1="21" x2="20" y2="21"/></svg>'
_SVG_TRASH = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>'
_SVG_REFRESH = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>'
_SVG_SETTINGS = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
_SVG_GRID = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'
_SVG_LAYOUT = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>'
_SVG_FORMAT = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>'


def _icon(svg: str, theme: _Theme) -> QIcon:
    """Render an SVG string colourised for the given theme."""
    return svg_to_icon(svg, size=16, color=theme.icon_color)


# ---------------------------------------------------------------------------
# Demo window
# ---------------------------------------------------------------------------

class DemoWindow(QMainWindow):
    """Test window demonstrating icons, callbacks, signals, and state."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FluentContextMenu — Demo")
        self.resize(920, 600)
        self._dark = False

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Controls
        ctrl = QHBoxLayout()
        self._toggle = QCheckBox("Dark Mode")
        self._toggle.toggled.connect(self._on_theme)
        ctrl.addWidget(self._toggle)
        ctrl.addStretch()
        root.addLayout(ctrl)

        # Demo areas
        cols = QHBoxLayout()

        grp1 = QGroupBox("Text Editor (right-click)")
        g1 = QVBoxLayout(grp1)
        self._editor = QTextEdit()
        self._editor.setPlaceholderText(
            "Right-click here → context menu with SVG icons.\n\n"
            "Toggle dark / light mode with the checkbox above.\n\n"
            "All three return-value patterns are demonstrated:\n"
            "  1) Callback  → status bar shows 'Callback: ...'\n"
            "  2) Signal    → status bar shows 'Signal: ...'\n"
            "  3) Reference → button text shows grid/snap state"
        )
        g1.addWidget(self._editor)
        cols.addWidget(grp1)

        grp2 = QGroupBox("Panel (right-click)")
        g2 = QVBoxLayout(grp2)
        self._panel = QWidget()
        self._panel.setMinimumSize(220, 200)
        g2.addWidget(self._panel)
        self._btn = QPushButton("Grid: ON | Snap: OFF")
        self._btn.setEnabled(False)
        g2.addWidget(self._btn)
        cols.addWidget(grp2)

        root.addLayout(cols)

        self._status = QLabel("Ready — right-click either area")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._status)

        self._build_menus()
        self._apply_app_theme()

    # -- Menu construction ---------------------------------------------------

    def _build_menus(self) -> None:
        t = DARK if self._dark else LIGHT

        # Editor menu (with icons)
        self._ed_menu = FluentContextMenu(dark_mode=self._dark)
        self._ed_menu.add_item("Cut", icon=_icon(_SVG_CUT, t), shortcut="Ctrl+X", callback=lambda: self._log("Cut"))
        self._ed_menu.add_item("Copy", icon=_icon(_SVG_COPY, t), shortcut="Ctrl+C", callback=lambda: self._log("Copy"))
        self._ed_menu.add_item("Paste", icon=_icon(_SVG_PASTE, t), shortcut="Ctrl+V", callback=lambda: self._log("Paste"))
        self._ed_menu.add_separator()
        self._ed_menu.add_item("Select All", icon=_icon(_SVG_SELECT, t), shortcut="Ctrl+A", callback=lambda: self._log("Select All"))
        self._ed_menu.add_separator()
        self._ed_menu.add_item("Undo", icon=_icon(_SVG_UNDO, t), shortcut="Ctrl+Z", callback=lambda: self._log("Undo"))
        self._ed_menu.add_item("Redo", icon=_icon(_SVG_REDO, t), shortcut="Ctrl+Y", callback=lambda: self._log("Redo"))
        self._ed_menu.add_separator()

        fmt = self._ed_menu.add_submenu("Format", icon=_icon(_SVG_FORMAT, t))
        fmt.add_item("Bold", icon=_icon(_SVG_BOLD, t), shortcut="Ctrl+B", callback=lambda: self._log("Bold"))
        fmt.add_item("Italic", icon=_icon(_SVG_ITALIC, t), shortcut="Ctrl+I", callback=lambda: self._log("Italic"))
        fmt.add_item("Underline", icon=_icon(_SVG_UNDERLINE, t), shortcut="Ctrl+U", callback=lambda: self._log("Underline"))

        self._ed_menu.add_separator()
        self._ed_menu.add_item("Delete", icon=_icon(_SVG_TRASH, t), enabled=False)
        self._ed_menu.action_triggered.connect(self._on_signal)
        self._ed_menu.attach(self._editor)

        # Panel menu (checkable items)
        self._pn_menu = FluentContextMenu(dark_mode=self._dark)
        self._pn_menu.add_item("Refresh", icon=_icon(_SVG_REFRESH, t), callback=lambda: self._log("Refresh"))
        self._pn_menu.add_item("Properties", icon=_icon(_SVG_SETTINGS, t), callback=lambda: self._log("Properties"))
        self._pn_menu.add_separator()
        self._grid_item = self._pn_menu.add_item("Show Grid", icon=_icon(_SVG_GRID, t), checkable=True, checked=True, callback=self._update_panel_btn)
        self._snap_item = self._pn_menu.add_item("Snap to Grid", icon=_icon(_SVG_GRID, t), checkable=True, checked=False, callback=self._update_panel_btn)
        self._pn_menu.add_separator()
        self._pn_menu.add_item("Reset Layout", icon=_icon(_SVG_LAYOUT, t), callback=lambda: self._log("Reset Layout"))
        self._pn_menu.action_triggered.connect(self._on_signal)
        self._pn_menu.attach(self._panel)

    def _rebuild_menus(self) -> None:
        self._ed_menu.detach(self._editor)
        self._pn_menu.detach(self._panel)
        grid_checked = self._grid_item.checked
        snap_checked = self._snap_item.checked
        self._build_menus()
        self._grid_item.checked = grid_checked
        self._snap_item.checked = snap_checked

    # -- Signal handler (pattern 2) ------------------------------------------

    def _on_signal(self, text: str, item_def: MenuItemDef) -> None:
        state = f"  [checked={item_def.checked}]" if item_def.checkable else ""
        self._status.setText(f'Signal: "{text}"{state}')

    # -- Reference handler (pattern 3) ---------------------------------------

    def _update_panel_btn(self) -> None:
        g = "ON" if self._grid_item.checked else "OFF"
        s = "ON" if self._snap_item.checked else "OFF"
        self._btn.setText(f"Grid: {g} | Snap: {s}")

    # -- Theme switching -----------------------------------------------------

    def _on_theme(self, checked: bool) -> None:
        self._dark = checked
        self._rebuild_menus()
        self._ed_menu.dark_mode = checked
        self._pn_menu.dark_mode = checked
        self._apply_app_theme()

    def _apply_app_theme(self) -> None:
        if self._dark:
            self.setStyleSheet("""
                QMainWindow { background: #1e1e1e; }
                QGroupBox { color: #e4e4e4; border: 1px solid #3d3d3d; border-radius: 8px; margin-top: 12px; padding-top: 16px; font-size: 13px; }
                QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }
                QTextEdit { background: #2b2b2b; color: #e4e4e4; border: 1px solid #3d3d3d; border-radius: 6px; padding: 8px; font-size: 13px; selection-background-color: #264f78; }
                QCheckBox { color: #e4e4e4; font-size: 13px; }
                QPushButton { background: #2b2b2b; color: #999; border: 1px solid #3d3d3d; border-radius: 6px; padding: 6px 16px; font-size: 13px; }
                QLabel { color: #888; font-size: 12px; }
            """)
            self._panel.setStyleSheet("background: #2d3250; border-radius: 8px;")
        else:
            self.setStyleSheet("""
                QMainWindow { background: #f3f3f3; }
                QGroupBox { color: #1a1a1a; border: 1px solid #e0e0e0; border-radius: 8px; margin-top: 12px; padding-top: 16px; font-size: 13px; }
                QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; }
                QTextEdit { background: #fff; color: #1a1a1a; border: 1px solid #e0e0e0; border-radius: 6px; padding: 8px; font-size: 13px; selection-background-color: #cce4ff; }
                QCheckBox { color: #1a1a1a; font-size: 13px; }
                QPushButton { background: #fff; color: #999; border: 1px solid #e0e0e0; border-radius: 6px; padding: 6px 16px; font-size: 13px; }
                QLabel { color: #888; font-size: 12px; }
            """)
            self._panel.setStyleSheet("background: #e0e7ff; border-radius: 8px;")

    def _log(self, text: str) -> None:
        self._status.setText(f'Callback: "{text}"')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())
