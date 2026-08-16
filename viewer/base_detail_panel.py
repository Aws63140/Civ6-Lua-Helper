"""
Base detail panel — shared infrastructure for detail views.

Provides:
  - Scroll area wrapper
  - Group box creation helper
  - Lua syntax highlighter
  - Copy-to-clipboard with feedback
  - Auto-height for example code area
  - _hl / _hl_yellow text highlight helpers
"""
import re

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QGroupBox, QPushButton,
    QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat


# ============================================================
# Lua syntax highlighter
# ============================================================
_KEYWORDS = [
    "function", "end", "local", "if", "then", "else", "elseif",
    "for", "while", "do", "return", "nil", "true", "false",
    "and", "or", "not", "in", "repeat", "until",
]


def _make_keyword_fmt():
    fmt = QTextCharFormat()
    fmt.setForeground(QColor("#c678dd"))
    fmt.setFontWeight(QFont.Weight.Bold)
    return fmt


def _build_highlight_rules():
    rules = []
    kw_fmt = _make_keyword_fmt()
    for kw in _KEYWORDS:
        rules.append((re.compile(rf"\b{kw}\b"), kw_fmt))

    comment_fmt = QTextCharFormat()
    comment_fmt.setForeground(QColor("#5c6370"))
    comment_fmt.setFontItalic(True)
    rules.append((re.compile(r"--[^\n]*"), comment_fmt))

    str_fmt = QTextCharFormat()
    str_fmt.setForeground(QColor("#98c379"))
    rules.append((re.compile(r'"[^"]*"'), str_fmt))
    rules.append((re.compile(r"'[^']*'"), str_fmt))

    num_fmt = QTextCharFormat()
    num_fmt.setForeground(QColor("#d19a66"))
    rules.append((re.compile(r"\b\d+\.?\d*\b"), num_fmt))

    func_fmt = QTextCharFormat()
    func_fmt.setForeground(QColor("#61afef"))
    rules.append((re.compile(r"\b\w+(?=\()"), func_fmt))

    return rules


_HIGHLIGHT_RULES = _build_highlight_rules()


class LuaSyntaxHighlighter(QSyntaxHighlighter):
    """Lua syntax highlighter for example code display."""

    def highlightBlock(self, text):
        for pattern, fmt in _HIGHLIGHT_RULES:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


# ============================================================
# Base detail panel
# ============================================================

class BaseDetailPanel(QWidget):
    """Base class for detail panels.

    Subclasses override:
      _get_default_title_text() — placeholder text when nothing selected
      _build_groups() — build section groups using _add_group()
      show_entry(entry) — render a data entry
      clear() — reset to empty state
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_example = ""
        self._example_text = None
        self._copy_btn = None
        self._highlighter = None

        # Scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        content_widget = QWidget()
        self._content_layout = QVBoxLayout(content_widget)
        self._content_layout.setContentsMargins(8, 8, 8, 8)
        self._content_layout.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidget(content_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(scroll)

        # Title
        self._title_label = QLabel(self._get_default_title_text())
        self._title_label.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self._title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._title_label.setWordWrap(True)
        self._content_layout.addWidget(self._title_label)

        # Build groups (overridden by subclass)
        self._build_groups()

    # ---- Hooks for subclasses ----

    def _get_default_title_text(self) -> str:
        return "选择一个条目查看详情"

    def _build_groups(self):
        """Override to build section groups via _add_group()."""
        pass

    # ---- Group helpers ----

    def _add_group(self, layout, title: str, font: QFont):
        """Create a standard group box with a label, return (group, label)."""
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(10, 14, 10, 10)
        label = QLabel()
        label.setFont(font)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setWordWrap(True)
        group_layout.addWidget(label)
        layout.addWidget(group)
        return group, label

    def _add_example_section(self):
        """Add example code block with Lua syntax highlighting and copy button.

        Sets self._example_text, self._copy_btn, self._highlighter.
        """
        self._example_group = QGroupBox("示例代码")
        example_layout = QVBoxLayout(self._example_group)
        example_layout.setContentsMargins(10, 14, 10, 10)

        self._example_text = QTextEdit()
        self._example_text.setReadOnly(True)
        self._example_text.setFont(QFont("Consolas", 13))
        self._example_text.setFixedHeight(55)
        self._example_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._highlighter = LuaSyntaxHighlighter(self._example_text.document())
        example_layout.addWidget(self._example_text)

        self._copy_btn = QPushButton("复制代码")
        self._copy_btn.setFixedSize(85, 30)
        self._copy_btn.setStyleSheet(
            "QPushButton { color: #abb2bf; border: 1px solid #3e4451; border-radius: 3px; padding: 3px 8px; font-size: 12px; }"
            "QPushButton:hover { background-color: #3e4451; }"
        )
        self._copy_btn.clicked.connect(self._copy_example)
        example_layout.addWidget(self._copy_btn, 0, Qt.AlignmentFlag.AlignLeft)

        self._content_layout.addWidget(self._example_group)

    # ---- Text highlight helpers ----

    @staticmethod
    def _hl(text: str) -> str:
        """Convert ==marked== text to blue HTML highlight."""
        return re.sub(r'==(.+?)==', r'<span style="color:#61afef">\1</span>', text)

    @staticmethod
    def _hl_yellow(text: str) -> str:
        """Convert --marked-- text to yellow HTML highlight."""
        return re.sub(r'--(.+?)--', r'<span style="color:#e5c07b">\1</span>', text)

    def _format_note(self, text: str) -> str:
        """应用备注高亮标记：==文本== 蓝色、--文本-- 黄色。"""
        return self._hl_yellow(self._hl(text))

    def _render_notes(self, notes, human_checked, unused_message):
        """Build the notes group HTML.

        Line order and colors:
          1. Verification status (always) — blue #61afef if human_checked, else yellow #e5c07b
          2. Unused warning (yellow) if unused_message
          3. First real note (blue) — the "[作用]" line
          4. Remaining notes (normal)
        Empty notes fall back to gray "无特殊注意事项".
        """
        lines = []
        if human_checked:
            lines.append("• <span style='color:#61afef'>[提醒] 此条目已由人工验证</span>")
        else:
            lines.append("• <span style='color:#e5c07b'>[提醒] 此条目尚未进行人工验证</span>")
        if unused_message:
            lines.append(f"• <span style='color:#e5c07b'>{self._format_note(unused_message)}</span>")
        if notes:
            for i, n in enumerate(notes):
                if i == 0:
                    lines.append(f"• <span style='color:#61afef'>{self._format_note(n)}</span>")
                else:
                    lines.append(f"• {self._format_note(n)}")
        else:
            lines.append("<span style='color:#5c6370'>无特殊注意事项</span>")
        return "<br>".join(lines)

    # ---- Example code resize ----

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._adjust_example_height()

    def _adjust_example_height(self):
        if self._example_text is None:
            return
        text = self._example_text.toPlainText()
        if not text:
            return
        line_count = text.count("\n") + 1
        line_height = self._example_text.fontMetrics().lineSpacing()
        ideal = max(55, min(line_count * line_height + 16, 400))
        self._example_text.setFixedHeight(ideal)

    # ---- Copy to clipboard ----

    def _copy_example(self):
        if not self._current_example or self._copy_btn is None:
            return
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._current_example)
        self._copy_btn.setText("已复制！")
        QTimer.singleShot(1500, lambda: self._copy_btn.setText("复制代码"))

    # ---- Clear ----

    def clear(self):
        """Clear all content. Override to add subclass-specific fields."""
        self._title_label.setText(self._get_default_title_text())
        self._title_label.setStyleSheet("")
        self._current_example = ""
        if self._example_text:
            self._example_text.setPlainText("")
