"""
搜索面板基类 —— SearchPanel / EventSearchPanel 的公共骨架

职责：
  - 搜索框 + 环境筛选行（QLineEdit + 清除按钮 + "环境:" 下拉框）
  - 150ms 单发防抖 QTimer（textChanged → 定时器 → _refresh_list）
  - _make_filter_row：固定宽度标签 + 下拉框的标准筛选行
  - 结果计数 QLabel
  - 结果 QListWidget（单选，选中即发射 entry_selected）
  - 结果列表项构建（UserRole 携带条目 + 按环境着色）
  - 环境筛选（"全部" 不限制，其余匹配自身 + Both）

子类通过钩子声明差异：
  - _LABEL_WIDTH：筛选标签固定宽度
  - _get_search_placeholder()：搜索框占位文本
  - _add_filter_rows(layout)：搜索行与结果计数之间的专属筛选行
  - _init_data()：构造完成后的数据初始化
  - _refresh_list(_)：列表刷新（各面板过滤逻辑不同，必须实现）
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QLabel, QComboBox, QHBoxLayout, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont

from .styles import AVAIL_COLORS


class BaseSearchPanel(QWidget):
    """左侧搜索面板基类。

    信号：
      entry_selected(dict): 选中条目时发射

    构造参数 data_loader 允许为 None（懒加载场景由子类处理）。
    """

    entry_selected = Signal(dict)

    # 筛选标签固定宽度（保证左对齐）；子类按需覆盖
    _LABEL_WIDTH = 50

    def __init__(self, data_loader=None, parent=None):
        super().__init__(parent)
        self._data_loader = data_loader
        self._updating = False
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._refresh_list)
        self._setup_ui()
        self._init_data()

    # ---- 子类钩子 ----

    def _get_search_placeholder(self) -> str:
        """搜索框占位文本（子类覆盖）。"""
        return "搜索..."

    def _add_filter_rows(self, layout):
        """在搜索行与结果计数之间添加专属筛选行（子类覆盖）。"""
        pass

    def _init_data(self):
        """构造完成后的数据初始化（子类覆盖）。"""
        pass

    def _refresh_list(self, _=None):
        """刷新结果列表（子类必须实现各自的过滤逻辑）。"""
        raise NotImplementedError

    # ---- UI 骨架 ----

    def _make_filter_row(self, label_text, combo):
        """创建一行筛选控件（固定宽度标签 + 下拉框）。"""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        label = QLabel(label_text)
        label.setFixedWidth(self._LABEL_WIDTH)
        row.addWidget(label)
        row.addWidget(combo, 1)
        return row

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # ---- 搜索框 + 环境筛选 ----
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText(self._get_search_placeholder())
        self._search_box.setFont(QFont("Microsoft YaHei", 11))
        self._search_box.setClearButtonEnabled(True)
        self._search_box.textChanged.connect(self._on_search_text_changed)
        row1.addWidget(self._search_box, 1)
        row1.addWidget(QLabel("环境:"))
        self._env_combo = QComboBox()
        self._env_combo.addItems(["全部", "UI", "GamePlay"])
        self._env_combo.currentTextChanged.connect(self._refresh_list)
        row1.addWidget(self._env_combo)
        layout.addLayout(row1)

        # ---- 子类专属筛选行 ----
        self._add_filter_rows(layout)

        # ---- 结果计数 ----
        self._count_label = QLabel()
        self._count_label.setFont(QFont("Microsoft YaHei", 9))
        self._count_label.setStyleSheet("color: #5c6370;")
        layout.addWidget(self._count_label)

        # ---- 结果列表 ----
        self._list_widget = QListWidget()
        self._list_widget.setFont(QFont("Consolas", 10))
        self._list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list_widget.currentItemChanged.connect(self._on_item_selected)
        layout.addWidget(self._list_widget)

    # ---- 通用行为 ----

    def _on_search_text_changed(self, text):
        self._search_timer.start(150)

    def _apply_env_filter(self, results):
        """按环境下拉框筛选结果（"全部" 不限制，其余匹配自身 + Both）。"""
        env_filter = self._env_combo.currentText()
        if env_filter != "全部":
            match_set = {env_filter, "Both"}
            results = [e for e in results if e.get("availability") in match_set]
        return results

    def _add_list_item(self, entry, text):
        """向结果列表追加一项（UserRole 携带条目并按环境着色）。"""
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, entry)
        avail = entry.get("availability", "")
        if avail in AVAIL_COLORS:
            item.setForeground(AVAIL_COLORS[avail])
        self._list_widget.addItem(item)

    def _on_item_selected(self, current, _):
        if current:
            entry = current.data(Qt.ItemDataRole.UserRole)
            if entry:
                self.entry_selected.emit(entry)
