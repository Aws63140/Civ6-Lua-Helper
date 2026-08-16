"""
Civ6 Lua Helper —— 文明6 Lua API 查询工具

功能：
  - 提供 PySide6 GUI 界面：函数查询 + 事件查询双页面（事件页懒加载）
  - 支持模糊搜索、层级筛选、事件系统筛选、环境筛选（UI/GamePlay）
  - 展示签名、参数、返回值、备注、示例代码（含 Lua 语法高亮）

运行方式：
  - Windows 命令行：python main.py
  - 双击 run.bat
"""
import sys
import os


def main():
    """程序入口：加载数据 → 创建 GUI → 运行事件循环。"""
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFont
    from viewer.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
