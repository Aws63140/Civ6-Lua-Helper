"""
布尔表达式搜索帮助对话框

由搜索面板搜索框右侧的 "?" 按钮唤起（非模态，可边搜索边对照查看），
内容为布尔搜索语法（AND / OR / NOT / 引号短语 / 括号分组）与示例。
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from .styles import DIALOG_STYLE

_HELP_WIDTH = 560

_HELP_TEXT = (
    "<h3 style='color:#e5c07b'>布尔表达式搜索</h3>"
    "<hr style='border-color:#3e4451'>"
    "<p><b>操作符</b>（必须全大写，小写会被当作普通搜索词）</p>"
    "<p>"
    "<tt style='color:#98c379'>AND</tt> —— 同时包含各搜索词。"
    "搜索词之间的空格等同于 AND，例如 <tt style='color:#98c379'>unit kill</tt> "
    "等价于 <tt style='color:#98c379'>unit AND kill</tt><br>"
    "<tt style='color:#98c379'>OR</tt> —— 包含其中任意一个搜索词，"
    "例如 <tt style='color:#98c379'>unit OR kill</tt><br>"
    "<tt style='color:#98c379'>NOT</tt> —— 排除某个搜索词，"
    "例如 <tt style='color:#98c379'>unit NOT kill</tt> "
    "表示包含 unit 但不包含 kill"
    "</p>"
    "<p><b>引号短语</b> —— 用英文双引号包裹可整体匹配词组，"
    "例如 <tt style='color:#98c379'>\"unit kill\"</tt> "
    "只匹配确切包含词组 unit kill 的条目</p>"
    "<p><b>括号分组</b> —— 用括号指定组合优先级，"
    "例如 <tt style='color:#98c379'>unit AND (kill OR combat)</tt> "
    "表示包含 unit，并且包含 kill 或 combat</p>"
    "<hr style='border-color:#3e4451'>"
    "<p style='color:#5c6370'>"
    "提示：搜索词不区分大小写。</p>"
)


class SearchHelpDialog(QDialog):
    """布尔表达式搜索帮助（非模态）。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("布尔表达式搜索帮助")
        self.setFixedWidth(_HELP_WIDTH)
        self.setStyleSheet(DIALOG_STYLE)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        label = QLabel(_HELP_TEXT)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        # 文本可选可复制（鼠标拖选，Ctrl+C 复制选中内容）
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label)

        close_btn = QPushButton("关 闭")
        close_btn.setFixedSize(100, 32)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignCenter)

        # 高度按内容自适应（宽固定 560）：避免最后一段提示文字被裁剪
        layout.activate()
        height = layout.heightForWidth(_HELP_WIDTH)
        if height > 0:
            self.setFixedHeight(height + 6)  # 留少量余量
        else:
            self.setFixedHeight(430)
