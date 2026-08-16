"""
Event detail panel — right-side panel for event details.
"""
from PySide6.QtGui import QFont

from .base_detail_panel import BaseDetailPanel


class EventDetailPanel(BaseDetailPanel):
    """Event detail panel.

    Sections:
      1. Title: eventSystem.eventName
      2. Callback signature
      3. Basic info: availability, eventSystem, eventType, category
      4. Callback parameters (numbered)
      5. Notes (with ==blue== and --yellow-- highlights)
      6. Example code (Lua syntax highlight + copy)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def _get_default_title_text(self) -> str:
        return "选择一个事件查看详情"

    def _build_groups(self):
        # Callback signature
        self._sig_group, self._signature_label = self._add_group(
            self._content_layout, "回调签名", QFont("Consolas", 13))

        # Basic info
        self._info_group, self._info_label = self._add_group(
            self._content_layout, "基本信息", QFont("Microsoft YaHei", 11))

        # Callback parameters
        self._args_group, self._args_label = self._add_group(
            self._content_layout, "回调参数", QFont("Consolas", 12))

        # Notes
        self._notes_group, self._notes_label = self._add_group(
            self._content_layout, "备注", QFont("Microsoft YaHei", 11))

        # Example code
        self._add_example_section()

        self._content_layout.addStretch(1)

    def show_entry(self, entry: dict):
        if not entry:
            return

        # Title: GameEvents.BuildingConstructed
        ev_sys = entry.get("eventSystem", "")
        ev_name = entry.get("eventName", "")
        self._title_label.setText(f"{ev_sys}.{ev_name}")
        self._title_label.setStyleSheet("color: #e5c07b;")

        # Callback signature
        self._signature_label.setText(entry.get("callbackSignature", ""))

        # Basic info
        avail = entry.get("availability", "")
        event_type = entry.get("eventType") or "未知"
        category = entry.get("category", "") or "未分类"
        self._info_label.setText(
            f"<span style='color:#61afef'>可用环境: {avail}</span><br>"
            f"事件系统: {ev_sys}<br>"
            f"事件类型: {event_type}<br>"
            f"分类: {category}"
        )

        # Callback parameters
        params = entry.get("callbackParams", [])
        if params:
            lines = []
            for i, p in enumerate(params, 1):
                name = p.get("name", "arg")
                p_type = p.get("type", "unknown").lstrip(":")
                desc = p.get("description", "")
                line = f"{i}. {name}: {p_type}"
                if desc:
                    line += f"    —— {desc}"
                lines.append(line)
            self._args_label.setText("\n".join(lines))
            self._args_label.setStyleSheet("")
        else:
            self._args_label.setText("无参数")
            self._args_label.setStyleSheet("color: #5c6370;")

        # Notes
        notes = list(entry.get("notes", []))
        unused_message = ""
        if entry.get("enrichUnused"):
            unused_message = "[提醒] 此事件无使用记录，可能无法正常工作，请谨慎使用"
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
        self._notes_label.setText("")
        if self._example_text:
            self._example_text.setPlainText("")
