"""
检查更新对话框

仅检查 GitHub Releases 版本，引导用户手动下载更新。
"""
import json
import re
import threading
import urllib.request
import urllib.error

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from .about_dialog import __version__
from .styles import DIALOG_STYLE


_GITHUB_API = "https://api.github.com/repos/Aws63140/Civ6-Lua-Helper/releases/latest"
_RELEASE_URL = "https://github.com/Aws63140/Civ6-Lua-Helper/releases"


class UpdateDialog(QDialog):
    """检查更新对话框（模态），仅检查版本并引导用户手动下载。"""

    # 网络结果必须通过信号回传：Qt 检测到发射方在非 GUI 线程时
    # 自动改为队列投递，槽函数由主线程事件循环执行。
    # 工作线程绝不能直接调用 _on_check_result/_on_check_error（会跨线程操作控件）。
    _check_done = Signal(str)
    _check_failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("检查更新")
        self.setFixedSize(450, 280)
        self.setStyleSheet(DIALOG_STYLE)
        self._setup_ui()
        self._check_done.connect(self._on_check_result)
        self._check_failed.connect(self._on_check_error)
        QTimer.singleShot(100, self._check_update)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel("<h3 style='color:#e5c07b'>检查更新</h3>")
        title.setTextFormat(Qt.RichText)
        layout.addWidget(title)

        layout.addWidget(QLabel("<hr style='border-color:#3e4451'>"))

        self._current_label = QLabel("<b>当前版本：</b>" + __version__)
        self._current_label.setTextFormat(Qt.RichText)
        self._current_label.setWordWrap(True)
        layout.addWidget(self._current_label)

        self._status_label = QLabel("<b>检查状态：</b>正在检查更新...")
        self._status_label.setTextFormat(Qt.RichText)
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        layout.addStretch(1)

        self._dl_btn = QPushButton("前往 Releases 页面下载")
        self._dl_btn.setFixedSize(180, 32)
        self._dl_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(_RELEASE_URL))
        )
        layout.addWidget(self._dl_btn, 0, Qt.AlignCenter)

        close_btn = QPushButton("关 闭")
        close_btn.setFixedSize(100, 32)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, 0, Qt.AlignCenter)

    def _check_update(self):
        """后台检查 GitHub Releases 版本。"""
        self._status_label.setText("<b>检查状态：</b>正在检查更新...")

        def _do_check():
            try:
                req = urllib.request.Request(
                    _GITHUB_API,
                    headers={"User-Agent": "Civ6LuaHelper"},
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())
                latest = data.get("tag_name", "")
                self._check_done.emit(latest)
            except urllib.error.HTTPError as e:
                msg = "没有找到 Releases" if e.code == 404 else (
                    "API 访问被限流，请稍后再试" if e.code == 403 else f"HTTP {e.code}"
                )
                self._check_failed.emit(msg)
            except Exception as e:
                self._check_failed.emit(str(e))

        threading.Thread(target=_do_check, daemon=True).start()

    def _on_check_result(self, latest: str):
        if not latest:
            self._status_label.setText(
                '<b>检查状态：</b><span style="color:#e5c07b">未找到版本信息</span>'
            )
            return
        cmp_result = self._compare_versions(latest, __version__)
        if cmp_result is None:
            self._status_label.setText(
                f"<b>最新版本：</b>{latest}<br>"
                '<span style="color:#e5c07b">版本号格式异常，无法比较，请前往 Releases 页面确认</span>'
            )
        elif cmp_result > 0:
            self._status_label.setText(
                f'<b>最新版本：</b><span style="color:#98c379">{latest}</span><br>'
                "发现新版本，点击下方按钮前往 Releases 页面下载。"
            )
        elif cmp_result == 0:
            self._status_label.setText(
                f"<b>最新版本：</b>{latest}<br>"
                '<span style="color:#5c6370">已是最新版本。</span>'
            )
        else:
            self._status_label.setText(
                f"<b>最新版本：</b>{latest}<br>"
                '<span style="color:#5c6370">当前版本高于远程版本。</span>'
            )

    def _on_check_error(self, msg: str):
        self._status_label.setText(
            f'<b>检查状态：</b><span style="color:#e5c07b">检查失败</span><br>'
            f'<span style="color:#5c6370">{msg}</span>'
        )

    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int | None:
        """比较版本号：1=v1 更新 / -1=v1 更旧 / 0=相同 / None=格式异常无法比较。

        三段式整数分段比较（v0.1.1 < v0.1.21 < v0.9.1 < v0.10.1 < v0.10.10 < v0.11.1），
        每段按整数比较；缺段补零兼容旧两段式 tag（v0.31 等同 v0.31.0）。
        """
        def _parse(v):
            s = str(v).strip().lstrip("vV")
            if not re.fullmatch(r"\d+(\.\d+){0,2}", s):
                raise ValueError(s)
            return [int(x) for x in s.split(".")]
        try:
            a, b = _parse(v1), _parse(v2)
        except ValueError:
            return None
        width = max(len(a), len(b))
        a += [0] * (width - len(a))
        b += [0] * (width - len(b))
        return (a > b) - (a < b)
