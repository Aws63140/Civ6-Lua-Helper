"""
左侧面板 —— 搜索与函数列表

职责：
  - 提供搜索框（模糊匹配最终函数名、displayName 与备注）
  - 提供层级筛选（根对象 → 函数A → 函数B）
  - 提供环境筛选（UI/GamePlay/全部）
  - 显示匹配结果列表

通用骨架（搜索框 + 环境筛选 + 防抖 + 结果列表）见 BaseSearchPanel。
"""
from PySide6.QtWidgets import QComboBox

from .base_search_panel import BaseSearchPanel


class SearchPanel(BaseSearchPanel):
    """
    左侧搜索面板。

    信号：
      entry_selected(dict): 选中函数时发射
    """

    # 筛选标签固定宽度（保证左对齐）
    _LABEL_WIDTH = 50

    def __init__(self, data_loader, parent=None):
        super().__init__(data_loader, parent)

    # ---- 子类钩子 ----

    def _get_search_placeholder(self) -> str:
        return "搜索函数名或备注..."

    def _add_filter_rows(self, layout):
        # ---- 根对象筛选 ----
        self._root_combo = QComboBox()
        self._root_combo.currentTextChanged.connect(self._on_root_changed)
        layout.addLayout(self._make_filter_row("根对象:", self._root_combo))

        # ---- 函数A筛选 ----
        self._func_a_combo = QComboBox()
        self._func_a_combo.setEnabled(False)
        self._func_a_combo.currentTextChanged.connect(self._on_func_a_changed)
        layout.addLayout(self._make_filter_row("函数A:", self._func_a_combo))

        # ---- 函数B筛选 ----
        self._func_b_combo = QComboBox()
        self._func_b_combo.setEnabled(False)
        self._func_b_combo.currentTextChanged.connect(self._on_func_b_changed)
        layout.addLayout(self._make_filter_row("函数B:", self._func_b_combo))

    def _init_data(self):
        self._populate_root_objects()

    # ---- 层级筛选联动 ----

    def _populate_root_objects(self):
        self._updating = True
        self._root_combo.addItem("全部")
        for root in self._data_loader.get_root_objects():
            self._root_combo.addItem(root)
        self._updating = False
        self._refresh_list()

    def _on_root_changed(self, root):
        if self._updating:
            return
        self._updating = True

        self._func_a_combo.clear()
        self._func_b_combo.clear()
        self._func_b_combo.setEnabled(False)

        if root == "全部":
            self._func_a_combo.setEnabled(False)
        else:
            self._func_a_combo.setEnabled(True)
            self._func_a_combo.addItem("全部")
            for func in self._data_loader.get_functions_a(root):
                self._func_a_combo.addItem(func)

        self._updating = False
        self._refresh_list()

    def _on_func_a_changed(self, func_a):
        if self._updating:
            return
        self._updating = True

        self._func_b_combo.clear()

        root = self._root_combo.currentText()
        if func_a == "全部" or not func_a:
            self._func_b_combo.setEnabled(False)
        else:
            funcs_b = self._data_loader.get_functions_b(root, func_a)
            if funcs_b:
                self._func_b_combo.setEnabled(True)
                self._func_b_combo.addItem("全部")
                for func in funcs_b:
                    self._func_b_combo.addItem(func)
            else:
                self._func_b_combo.setEnabled(False)

        self._updating = False
        self._refresh_list()

    def _on_func_b_changed(self, _):
        if self._updating:
            return
        self._refresh_list()

    # ---- 列表刷新 ----

    def _refresh_list(self, _=None):
        query = self._search_box.text().strip()
        root = self._root_combo.currentText()
        func_a = self._func_a_combo.currentText()
        func_b = self._func_b_combo.currentText()

        # "全部" 视为空（不限制）
        root_f = "" if root == "全部" else root
        func_a_f = "" if func_a == "全部" else func_a
        func_b_f = "" if func_b == "全部" else func_b

        # 获取层级筛选结果
        if query:
            results, error = self._data_loader.search(query)
            if error:
                # 布尔表达式语法错误：显示提示并清空列表
                self._show_count(f"表达式语法错误：{error}", error=True)
                self._list_widget.clear()
                return
            if root_f:
                results = [e for e in results if e.get("table") == root_f]
                if func_a_f:
                    results = [e for e in results if e.get("functionA") == func_a_f]
                    if func_b_f:
                        results = [e for e in results if e.get("functionB") == func_b_f]
        else:
            results = self._data_loader.get_entries(root_f, func_a_f, func_b_f)

        # 按环境筛选（"全部" 不限制）
        results = self._apply_env_filter(results)

        self._show_count(f"找到 {len(results)} 个函数")

        # 更新列表
        self._list_widget.clear()
        for entry in results:
            display = entry.get("displayName", "")
            avail = entry.get("availability", "")
            self._add_list_item(entry, f"{display}  [{avail}]")
