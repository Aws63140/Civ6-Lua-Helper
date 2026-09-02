"""
集中样式 —— 全局 QSS 样式表与颜色常量

包含：One Dark 主题（主窗口）、对话框样式（检查更新 / 关于）、
可用环境颜色映射（搜索结果列表项前景色）。
"""
from PySide6.QtGui import QColor


# ============================================================
# One Dark 暗色主题样式表（主窗口使用）
# ============================================================
DARK_THEME = """
    QMainWindow, QWidget {
        background-color: #282c34;
        color: #abb2bf;
    }
    QLineEdit {
        background-color: #1e2127;
        border: 1px solid #3e4451;
        border-radius: 4px;
        padding: 6px;
        color: #abb2bf;
    }
    QLineEdit:focus {
        border-color: #61afef;
    }
    QListWidget {
        background-color: #1e2127;
        border: 1px solid #3e4451;
        border-radius: 4px;
        color: #abb2bf;
    }
    QListWidget::item:selected {
        background-color: #3e4451;
    }
    QListWidget::item:hover {
        background-color: #2c313a;
    }
    QComboBox {
        background-color: #1e2127;
        border: 1px solid #3e4451;
        border-radius: 4px;
        padding: 4px;
        color: #abb2bf;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox QAbstractItemView {
        background-color: #1e2127;
        color: #abb2bf;
        selection-background-color: #3e4451;
    }
    QGroupBox {
        border: 1px solid #3e4451;
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 12px;
        color: #e5c07b;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
    }
    QTextEdit {
        background-color: #1e2127;
        border: 1px solid #3e4451;
        border-radius: 4px;
        color: #abb2bf;
    }
    QScrollArea {
        border: none;
    }
    QSplitter::handle {
        background-color: #3e4451;
        width: 2px;
    }
    QLabel {
        color: #abb2bf;
    }
    QStatusBar {
        background-color: #1e2127;
        color: #5c6370;
    }
    QMenuBar {
        background-color: #1e2127;
        color: #abb2bf;
        border-bottom: 1px solid #3e4451;
    }
    QMenuBar::item:selected {
        background-color: #3e4451;
    }
    QMenu {
        background-color: #1e2127;
        color: #abb2bf;
        border: 1px solid #3e4451;
        padding-left: 4px;
        padding-top: 2px;
        padding-bottom: 2px;
    }
    QMenu::item {
        padding: 4px 24px 4px 12px;
        margin-top: 1px;
        margin-bottom: 1px;
    }
    QMenu::item:selected {
        background-color: #3e4451;
        color: #abb2bf;
    }
    QToolButton#boolSearchHelpButton {
        background-color: #1e2127;
        border: 1px solid #3e4451;
        border-radius: 12px;
        color: #61afef;
        font-weight: bold;
        font-size: 13px;
    }
    QToolButton#boolSearchHelpButton:hover {
        border-color: #61afef;
        background-color: #3e4451;
    }
    QTabBar {
        background-color: transparent;
    }
    QTabBar::tab {
        background-color: transparent;
        color: #5c6370;
        padding: 4px 16px;
        margin-right: 4px;
        border: 1px solid transparent;
        border-top: 2px solid transparent;
        border-radius: 4px;
        font-size: 13px;
    }
    QTabBar::tab:selected {
        background-color: #1e2127;
        color: #61afef;
        border-color: #3e4451;
        border-top: 2px solid #61afef;
    }
    QTabBar::tab:hover:!selected {
        background-color: #2c313a;
        color: #abb2bf;
    }
"""


# ============================================================
# 检查更新对话框样式（含 QPushButton:disabled 规则）
# ============================================================
DIALOG_STYLE = """
    QDialog {
        background-color: #282c34;
        color: #abb2bf;
        border: 1px solid #3e4451;
        border-radius: 8px;
    }
    QLabel { color: #abb2bf; }
    QPushButton {
        background-color: #3e4451;
        color: #abb2bf;
        border: 1px solid #61afef;
        border-radius: 4px;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #61afef;
        color: #282c34;
    }
    QPushButton:disabled {
        color: #5c6370;
        border-color: #3e4451;
    }
"""


# ============================================================
# 关于对话框样式（与 DIALOG_STYLE 几乎相同，仅缺 QPushButton:disabled 规则）
# ============================================================
ABOUT_DIALOG_STYLE = """
    QDialog {
        background-color: #282c34;
        color: #abb2bf;
        border: 1px solid #3e4451;
        border-radius: 8px;
    }
    QLabel {
        color: #abb2bf;
    }
    QPushButton {
        background-color: #3e4451;
        color: #abb2bf;
        border: 1px solid #61afef;
        border-radius: 4px;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #61afef;
        color: #282c34;
    }
"""


# 可用环境颜色映射（搜索结果列表项前景色）
AVAIL_COLORS = {
    "Both": QColor("#98c379"),
    "UI": QColor("#61afef"),
    "GamePlay": QColor("#c678dd"),
}
