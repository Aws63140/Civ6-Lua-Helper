"""
关于对话框
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from .styles import ABOUT_DIALOG_STYLE

__version__ = "v0.33.0"

_PROJECT_URL = "https://github.com/Aws63140/Civ6-Lua-Helper"
_DATA_SOURCE_URL = "https://github.com/Sumcam-L"

_ABOUT_TEXT = (
    "<h3 style='color:#e5c07b'>文明6 Lua 辅助工具</h3>"
    f"<p>版本: {__version__}</p>"
    "<p>作者: Awase</p>"
    "<hr style='border-color:#3e4451'>"
    "<p><b>项目地址</b></p>"
    f"<p><a href='{_PROJECT_URL}' style='color:#61afef'>{_PROJECT_URL}</a></p>"
    "<hr style='border-color:#3e4451'>"
    "<p><b>数据来源</b></p>"
    f"<p>社区整理的 Civ6 Lua 函数+事件数据集<br><a href='{_DATA_SOURCE_URL}' style='color:#61afef'>夏凉凉凉</a> 分享的 skill 文档。</p>"
    "<hr style='border-color:#3e4451'>"
    "<p><b>警告：此工具尚未完成，数据仅作参考，不可完全信任！</b><br>"
    "多数情况下，可参考签名、参数、返回值和示例代码，但请辩证看待备注信息！<br>"
    "作者一人很难完成 4000+ 条数据的实际验证，如果你发现错误信息，欢迎提供反馈！</p>"
)


class AboutDialog(QDialog):
    """关于对话框（模态）。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        self.setFixedWidth(420)
        self.setStyleSheet(ABOUT_DIALOG_STYLE)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        label = QLabel(_ABOUT_TEXT)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        label.linkActivated.connect(lambda url: QDesktopServices.openUrl(QUrl(url)))
        layout.addWidget(label)

        ok_btn = QPushButton("确 定")
        ok_btn.setFixedSize(100, 32)
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, 0, Qt.AlignmentFlag.AlignCenter)

        # 高度按内容自适应（宽固定 420）：避免最后一段文字被裁剪
        layout.activate()
        height = layout.heightForWidth(420)
        if height > 0:
            self.setFixedHeight(height + 6)  # 留少量余量
        else:
            self.setFixedHeight(392)
