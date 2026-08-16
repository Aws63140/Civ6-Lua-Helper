# 文明6 Lua 辅助工具

查询 Civilization VI 的 Lua 函数和事件的辅助工具，免去模组作者频繁翻阅文档的麻烦。

提供开箱即用的 exe 与完整 Python 源码两种使用方式。

## 下载

前往 [Releases](https://github.com/Aws63140/Civ6-Lua-Helper/releases) 下载最新版 `Civ6LuaHelper.exe`，双击运行即可。

## 从源码运行

- Python 3.10+
- 安装依赖：`pip install -r requirements.txt`
- 启动：`python main.py`（或双击 `run.bat`）

## 使用说明

| 功能 | 说明 |
|------|------|
| 双窗口切换 | 窗口菜单切换 **函数查询** 和 **事件查询** 两个独立工作区 |
| 函数搜索 | 模糊搜索函数名与备注，多个关键词用空格分隔（AND 语义） |
| 函数筛选 | 按根对象 → 函数A → 函数B 层级筛选，按环境（UI/GamePlay）筛选 |
| 事件搜索 | 模糊搜索事件名与备注，多个关键词用空格分隔（AND 语义） |
| 事件筛选 | 按事件系统（Events/GameEvents/LuaEvents）和环境筛选 |
| 详情展示 | 签名、参数、返回值、备注（支持高亮标记）、示例代码（Lua 语法高亮 + 一键复制） |

## 更新

工具启动后点击 **帮助 → 检查更新**。

## 数据说明

数据仅供参考，使用时请辩证看待。
作者一人很难完成 4000+ 条数据的实际验证，如果你发现错误信息，欢迎提供反馈！

### 数据来源

| 来源 | 说明 |
|------|------|
| **Civ VI Modding Companion 2.0.xlsx** | 社区整理的 Civ6 Lua 函数+事件数据集 |
| **夏凉凉凉's civ6-modding skill files** | 夏凉凉凉分享的 skill 文档 |

### 数据文件

- `data/api_enhanced.json` — 86 个对象 / 命名空间，3273 个函数条目
- `data/events_enhanced.json` — 1045 个事件（Events 483 / GameEvents 82 / LuaEvents 480）
