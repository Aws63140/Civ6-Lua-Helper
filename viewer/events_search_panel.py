"""
Event search panel — left-side panel for searching and filtering events.

Layout:
  Row 1: search box + environment filter
  Row 2: event system filter
  Followed by result list

Shared skeleton (search box + env filter + debounce + result list) in BaseSearchPanel.
"""
from PySide6.QtWidgets import QComboBox

from .base_search_panel import BaseSearchPanel


class EventSearchPanel(BaseSearchPanel):
    """Event search panel.

    Signals:
      entry_selected(dict): emitted when an event is selected
    """

    # Filter label fixed width (wider than the API panel: "事件系统:" label)
    _LABEL_WIDTH = 62

    # ---- Subclass hooks ----

    def _get_search_placeholder(self) -> str:
        return "搜索事件名或备注..."

    def _add_filter_rows(self, layout):
        # Row 2: event system filter
        self._sys_combo = QComboBox()
        self._sys_combo.currentTextChanged.connect(self._refresh_list)
        layout.addLayout(self._make_filter_row("事件系统:", self._sys_combo))

    def _init_data(self):
        if self._data_loader is not None:
            self._populate_filters()

    # ---- Lazy loading ----

    def set_data_loader(self, loader):
        """Set data loader after construction (lazy loading support)."""
        self._data_loader = loader
        self._populate_filters()
        self._refresh_list()

    def _populate_filters(self):
        if self._data_loader is None:
            return
        self._updating = True
        self._sys_combo.clear()
        self._sys_combo.addItem("全部")
        for sys in self._data_loader.get_event_systems():
            self._sys_combo.addItem(sys)
        self._updating = False

    # ---- Search / filter ----

    def _refresh_list(self, _=None):
        if self._data_loader is None:
            return

        query = self._search_box.text().strip()
        sys_filter = self._sys_combo.currentText()
        env_filter = self._env_combo.currentText()

        sys_f = "" if sys_filter == "全部" else sys_filter
        env_f = "" if env_filter == "全部" else env_filter

        results, error = self._data_loader.search(query, event_system=sys_f, availability=env_f)
        if error:
            # 布尔表达式语法错误：显示提示并清空列表
            self._show_count(f"表达式语法错误：{error}", error=True)
            self._list_widget.clear()
            return

        self._show_count(f"找到 {len(results)} 个事件")

        self._list_widget.clear()
        for event in results:
            ev_sys = event.get("eventSystem", "")
            ev_name = event.get("eventName", "")
            avail = event.get("availability", "")
            self._add_list_item(event, f"{ev_sys}.{ev_name}  [{avail}]")
