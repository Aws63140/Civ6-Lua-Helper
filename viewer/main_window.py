"""
主窗口 —— 左右分栏布局，支持多页面切换（API 查询 + 事件查询）

职责：
  - 加载 API 数据
  - 创建左侧搜索面板和右侧详情面板（API / Events 各一套）
  - 用可拖拽分割器连接两个面板
  - 应用全局暗色主题样式
  - 在状态栏显示加载统计信息
  - 窗口菜单支持页面切换（QStackedWidget）
"""
from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QStatusBar, QDialog, QLabel, QVBoxLayout, QPushButton, QWidget,
    QStackedWidget
)
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup

from .data_loader import ApiDataLoader
from .search_panel import SearchPanel
from .detail_panel import DetailPanel
from .events_loader import EventDataLoader
from .events_search_panel import EventSearchPanel
from .events_detail_panel import EventDetailPanel
from .styles import DARK_THEME


class MainWindow(QMainWindow):
    """
    应用主窗口，支持多页面切换。

    QStackedWidget:
      0: 函数查询窗口（搜索 + 详情）
      1: 事件查询窗口（搜索 + 详情）— 懒加载
    """

    def __init__(self, data_path=None):
        super().__init__()
        self.setWindowTitle("文明6 Lua 辅助工具")
        self.setMinimumSize(1100, 700)
        self.resize(1400, 850)

        self._data_loader = ApiDataLoader(data_path)

        # Startup dim overlay (created on timer; tracks window resizes while alive)
        self._startup_overlay = None

        # Events page — lazy initialized
        self._event_loader = None
        self._events_search = None
        self._events_detail = None
        self._events_page_ready = False

        self.setStyleSheet(DARK_THEME)
        self._setup_ui()
        self._show_startup_dialog()

    # ---- Window menu ----

    def _on_window_changed(self, action):
        """Switch between API and Events pages."""
        page_index = action.data()

        if page_index == 1 and not self._events_page_ready:
            self._init_events_page()

        self._stack.setCurrentIndex(page_index)

    # ---- Events page lazy init ----

    def _init_events_page(self):
        """Lazy-initialize the events page on first switch."""
        self._event_loader = EventDataLoader()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setChildrenCollapsible(False)

        self._events_search = EventSearchPanel(self._event_loader)
        self._events_search.setMinimumWidth(350)
        splitter.addWidget(self._events_search)

        self._events_detail = EventDetailPanel()
        self._events_detail.setMinimumWidth(400)
        splitter.addWidget(self._events_detail)

        splitter.setSizes([490, 910])

        # Replace placeholder (widget at index 1)
        placeholder = self._stack.widget(1)
        self._stack.removeWidget(placeholder)
        placeholder.deleteLater()
        self._stack.insertWidget(1, splitter)

        # Connect signals
        self._events_search.entry_selected.connect(self._events_detail.show_entry)

        self._events_page_ready = True

        # Update status bar to show combined stats
        self._update_status_bar()

    def _update_status_bar(self):
        """Update status bar with current data source stats."""
        api_total = len(self._data_loader.entries)
        api_roots = len(self._data_loader.root_index)

        if self._event_loader is not None:
            ev_total = self._event_loader.total_events
            ev_enriched = self._event_loader.enriched_count
            msg = f"已加载 {api_total} 个函数，{api_roots} 个根对象 | {ev_total} 个事件，{ev_enriched} 个已验证"
        else:
            msg = f"已加载 {api_total} 个函数，{api_roots} 个根对象"

        self.statusBar().showMessage(msg)

    # ---- Update dialog ----

    def _check_update(self):
        from .update_dialog import UpdateDialog
        dialog = UpdateDialog(self)
        dialog.exec()

    # ---- UI setup ----

    def _setup_ui(self):
        # ---- Menu bar ----
        menu_bar = self.menuBar()

        # Window menu
        window_menu = menu_bar.addMenu("窗口(&W)")
        self._window_group = QActionGroup(self)
        self._window_group.setExclusive(True)

        api_action = QAction("函数查询窗口", self)
        api_action.setCheckable(True)
        api_action.setChecked(True)
        api_action.setData(0)
        self._window_group.addAction(api_action)
        window_menu.addAction(api_action)

        events_action = QAction("事件查询窗口", self)
        events_action.setCheckable(True)
        events_action.setData(1)
        self._window_group.addAction(events_action)
        window_menu.addAction(events_action)

        self._window_group.triggered.connect(self._on_window_changed)

        # Help menu
        help_menu = menu_bar.addMenu("帮助(&H)")

        check_action = help_menu.addAction("检查更新...")
        check_action.triggered.connect(self._check_update)

        about_action = help_menu.addAction("关于此工具(&A)")
        about_action.triggered.connect(self._show_about_dialog)

        # ---- Central content area ----
        self._stack = QStackedWidget()

        # Page 0: API query window
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setChildrenCollapsible(False)

        self._search_panel = SearchPanel(self._data_loader)
        self._search_panel.setMinimumWidth(350)
        splitter.addWidget(self._search_panel)

        self._detail_panel = DetailPanel()
        self._detail_panel.setMinimumWidth(400)
        splitter.addWidget(self._detail_panel)

        splitter.setSizes([490, 910])
        self._stack.addWidget(splitter)

        # Page 1: Events placeholder (replaced on first switch)
        self._stack.addWidget(QWidget())

        self.setCentralWidget(self._stack)

        # Signals
        self._search_panel.entry_selected.connect(self._detail_panel.show_entry)

        # Status bar
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._update_status_bar()

    def _show_about_dialog(self):
        from .about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()

    def _show_startup_dialog(self):
        """Show startup dialog after main window is displayed."""
        QTimer.singleShot(0, self._create_startup_overlay)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 启动遮罩是一次性子控件，不会自动跟随窗口尺寸，需在此同步覆盖区域
        if self._startup_overlay is not None:
            self._startup_overlay.setGeometry(self.rect())

    def _create_startup_overlay(self):
        """Create semi-transparent overlay + centered dialog."""
        overlay = QWidget(self)
        overlay.setGeometry(self.rect())
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 160);")
        overlay.show()
        self._startup_overlay = overlay

        dialog = QDialog(self)
        dialog.setWindowTitle("文明6 Lua 辅助工具")
        dialog.setMinimumWidth(420)
        dialog.setStyleSheet(DARK_THEME + """
            QDialog {
                background-color: #282c34;
                border: 1px solid #3e4451;
                border-radius: 8px;
            }
        """)

        def close_overlay(_=None):
            self._startup_overlay = None
            overlay.deleteLater()

        dialog.finished.connect(close_overlay)

        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setContentsMargins(24, 20, 24, 20)
        dlg_layout.setSpacing(12)

        text = (
            "<h3 style='color:#e5c07b'>欢迎使用 文明6 Lua 辅助工具</h3>"
            "<hr style='border-color:#3e4451'>"
            "<p><b>警告：此工具尚未完成，数据仅作参考，不可完全信任！</b><br>"
            "多数情况下，可参考签名、参数、返回值和示例代码，但请辩证看待备注信息！<br>"
            "作者一人很难完成 4000+ 条数据的实际验证，如果你发现错误信息，欢迎提供反馈！</p>"
        )

        label = QLabel(text)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setStyleSheet("color: #abb2bf;")
        dlg_layout.addWidget(label)

        ok_btn = QPushButton("确 定")
        ok_btn.setFixedSize(100, 32)
        ok_btn.setStyleSheet(
            "QPushButton { background-color: #3e4451; color: #abb2bf; border: 1px solid #61afef; border-radius: 4px; font-size: 13px; }"
            "QPushButton:hover { background-color: #61afef; color: #282c34; }"
        )
        ok_btn.clicked.connect(dialog.accept)
        dlg_layout.addWidget(ok_btn, 0, Qt.AlignmentFlag.AlignCenter)

        dialog.adjustSize()
        geo = self.geometry()
        x = geo.x() + (geo.width() - dialog.width()) // 2
        y = geo.y() + (geo.height() - dialog.height()) // 2
        dialog.move(x, y)

        dialog.show()
