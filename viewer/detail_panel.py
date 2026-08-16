"""
API detail panel — right-side panel for API function details.
"""
from PySide6.QtGui import QFont

from .base_detail_panel import BaseDetailPanel


class DetailPanel(BaseDetailPanel):
    """API function detail panel.

    Sections:
      1. Title (displayName)
      2. Function signature
      3. Basic info (availability, table, type, invoke)
      4. Parameters (numbered)
      5. Returns (numbered)  — API-specific
      6. Notes (with ==blue== and --yellow-- highlights)
      7. Example code (Lua syntax highlight + copy)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def _get_default_title_text(self) -> str:
        return "选择一个函数查看详情"

    def _build_groups(self):
        # Function signature
        self._sig_group, self._signature_label = self._add_group(
            self._content_layout, "函数签名", QFont("Consolas", 13))

        # Basic info
        self._info_group, self._info_label = self._add_group(
            self._content_layout, "基本信息", QFont("Microsoft YaHei", 11))

        # Parameters
        self._args_group, self._args_label = self._add_group(
            self._content_layout, "参数", QFont("Consolas", 12))

        # Returns — API-specific
        self._returns_group, self._returns_label = self._add_group(
            self._content_layout, "返回值", QFont("Consolas", 12))

        # Notes
        self._notes_group, self._notes_label = self._add_group(
            self._content_layout, "备注", QFont("Microsoft YaHei", 11))

        # Example code
        self._add_example_section()

        self._content_layout.addStretch(1)

    @staticmethod
    def _get_final_args(entry: dict) -> list:
        """Get the deepest function's args (argsC > argsB > argsA)."""
        for suffix in ("C", "B", "A"):
            func = entry.get(f"function{suffix}", "")
            if func:
                return entry.get(f"args{suffix}", [])
        return entry.get("argsA", [])

    def show_entry(self, entry: dict):
        if not entry:
            return

        self._title_label.setText(entry.get("displayName", ""))
        self._title_label.setStyleSheet("color: #e5c07b;")

        self._signature_label.setText(entry.get("signature", ""))

        avail = entry.get("availability", "")
        self._info_label.setText(
            f"<span style='color:#61afef'>可用环境: {avail}</span><br>"
            f"类别: {entry.get('table', '')}<br>"
            f"类型: {entry.get('type', '')}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;—— {entry.get('typeNote', '')}<br>"
            f"调用方式: {entry.get('invoke', '')}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;—— {entry.get('invokeNote', '')}"
        )

        # Parameters
        args = self._get_final_args(entry)
        if args:
            lines = []
            for i, a in enumerate(args, 1):
                name = a.get("name", "arg")
                a_type = a.get("type", "unknown").lstrip(":")
                desc = a.get("description", "")
                line = f"{i}. {name}: {a_type}"
                if desc:
                    line += f"    —— {desc}"
                lines.append(line)
            self._args_label.setText("\n".join(lines))
            self._args_label.setStyleSheet("")
        else:
            self._args_label.setText("无参数")
            self._args_label.setStyleSheet("color: #5c6370;")

        # Returns
        returns = entry.get("returns", [])
        if returns:
            lines = []
            for i, r in enumerate(returns, 1):
                name = r.get("name", "result")
                r_type = r.get("type", "unknown").lstrip(":")
                desc = r.get("description", "")
                line = f"{i}. {name}: {r_type}"
                if desc:
                    line += f"    —— {desc}"
                lines.append(line)
            self._returns_label.setText("\n".join(lines))
            self._returns_label.setStyleSheet("")
        else:
            self._returns_label.setText("无返回值")
            self._returns_label.setStyleSheet("color: #5c6370;")

        # Notes
        notes = list(entry.get("notes", []))
        unused_message = ""
        if entry.get("enrichUnused"):
            unused_message = "[提醒] 此函数无使用记录，可能无法正常工作，请谨慎使用"
        self._notes_label.setText(self._render_notes(notes, entry.get("humanChecked"), unused_message))
        self._notes_label.setStyleSheet("")

        # Example code
        self._current_example = entry.get("exampleCode", "")
        self._example_text.setPlainText(self._current_example)
        self._adjust_example_height()

    def clear(self):
        super().clear()
        self._signature_label.setText("")
        self._info_label.setText("")
        self._args_label.setText("")
        self._returns_label.setText("")
        self._notes_label.setText("")
        if self._example_text:
            self._example_text.setPlainText("")
