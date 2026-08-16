"""
viewer 包 —— Civ6 Lua Helper 的 GUI 模块

模块说明：
  - main_window: 主窗口（左右分栏布局 + 多页面切换 + 暗色主题 + 菜单栏）
  - styles: 集中样式（One Dark 主题 QSS、对话框 QSS、环境颜色映射）
  - data_loader: API 数据加载与搜索（模糊搜索 + 分类查询）
  - events_loader: 事件数据加载与搜索
  - base_search_panel: 搜索面板基类（搜索框 + 环境筛选 + 防抖 + 结果列表）
  - search_panel: 左侧 API 搜索面板（层级筛选：根对象 → 函数A → 函数B）
  - events_search_panel: 左侧事件搜索面板（事件系统筛选）
  - base_detail_panel: 详情面板基类（滚动区域 + Lua 语法高亮 + 复制按钮 + 备注高亮渲染）
  - detail_panel: 右侧 API 详情面板（签名 + 参数 + 返回值 + 备注 + 示例代码）
  - events_detail_panel: 右侧事件详情面板（回调签名 + 回调参数 + 备注 + 示例代码）
  - about_dialog: 关于对话框（应用信息 + 版本 + 免责声明）
  - update_dialog: 检查更新对话框（GitHub Releases 版本检查 + 引导下载）
"""
