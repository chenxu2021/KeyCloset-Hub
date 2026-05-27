"""
KeyCloset Hub - 应用入口与生命周期管理
协调应用启动、解锁、锁定、退出等完整生命周期。

生命周期流程:
  1. 初始化数据目录和数据库
  2. 弹出 LoginDialog 验证主密码
  3. 验证通过 → 创建 MainWindow
  4. 运行中监控用户活动，5 分钟无操作自动锁定
  5. 锁定时隐藏主窗口 → 重新弹出 LoginDialog
  6. 退出时清理数据库连接并标记锁定状态

空闲锁定策略:
  - 使用 QTimer 每 500ms 检测最后活动时间戳
  - 任何鼠标移动、键盘按键、窗口焦点变化都刷新时间戳
  - 超过 AUTO_LOCK_TIMEOUT (5 分钟) 触发锁定
"""

import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from .database import Database
from .ui.login_dialog import LoginDialog
from .ui.main_window import MainWindow
from .utils import get_db_path

# 自动锁定时间 (毫秒) — 5 分钟
AUTO_LOCK_TIMEOUT = 5 * 60 * 1000


class KeyClosetApp(QApplication):
    """
    KeyCloset Hub 应用主类。

    继承 QApplication，管理全局状态和空闲锁定定时器。
    """

    def __init__(self, argv):
        super().__init__(argv)

        # 设置应用元信息
        self.setApplicationName("KeyCloset Hub")
        self.setOrganizationName("KeyCloset")

        # 数据层
        self.database = Database(get_db_path())

        # UI 引用
        self._main_window: MainWindow = None
        self._login_dialog: LoginDialog = None

        # 空闲锁定
        self._last_activity = 0
        self._idle_timer = QTimer()
        self._idle_timer.timeout.connect(self._check_idle)

        # 启动流程
        self._show_login()

    # ---------- 应用生命周期 ----------

    def _show_login(self):
        """
        显示登录/解锁对话框。

        首次使用时引导设置主密码，之后验证解锁。
        取消对话框即退出应用。
        """
        self._login_dialog = LoginDialog(self.database)
        # 先断开所有旧的 unlock_success 连接，防止重复触发
        try:
            self._login_dialog.unlock_success.disconnect()
        except TypeError:
            pass
        self._login_dialog.unlock_success.connect(self._on_unlocked)
        self._login_dialog.finished.connect(self._on_login_finished)
        self._login_dialog.show()

    def _on_unlocked(self, master_password: str):
        """
        解锁成功后的回调。
        注意：不在此处关闭 login_dialog，因为 accept() 会正常关闭它。
        close() 会触发 finished(Rejected) 导致 _on_login_finished 退出。

        Args:
            master_password: 已验证正确的主密码
        """
        # 标记 login_dialog 即将由 accept() 正常关闭，不应退出
        self._login_success = True

        # 创建主窗口
        self._main_window = MainWindow(
            database=self.database,
            master_password=master_password,
            lock_callback=self.lock,
        )
        self._main_window.show()

        # 启动空闲监控
        self._start_idle_monitor()

    def _on_login_finished(self, result: int):
        """
        登录对话框关闭时的回调。

        Args:
            result: QDialog.Accepted (1) 或 QDialog.Rejected (0)
        """
        # 解锁成功标记为 True，不退出
        if getattr(self, '_login_success', False):
            self._login_success = False
            return

        # 如果对话框被取消且没有主窗口打开，则退出
        if not self._main_window:
            self.quit()

    def lock(self):
        """
        锁定应用:
          1. 隐藏主窗口
          2. 清除主窗口中的解密数据
          3. 停止空闲监控定时器
          4. 重新弹出解锁对话框
        """
        if self._main_window:
            self._main_window.lock()
            self._main_window.hide()

        self._stop_idle_monitor()

        # 标记数据库为锁定状态
        self.database.set_setting("locked", "1")

        # 重新弹出解锁对话框 (只会连接 _on_unlocked)
        self._show_login()

    # ---------- 空闲锁定 ----------

    def _start_idle_monitor(self):
        """启动空闲监控定时器 (500ms 间隔)。"""
        self._last_activity = self._current_time_ms()
        self._idle_timer.start(500)

    def _stop_idle_monitor(self):
        """停止空闲监控定时器。"""
        self._idle_timer.stop()

    def _check_idle(self):
        """
        检查空闲时间是否超过阈值。

        如果超过 AUTO_LOCK_TIMEOUT (5分钟)，触发锁定。
        """
        elapsed = self._current_time_ms() - self._last_activity
        if elapsed > AUTO_LOCK_TIMEOUT:
            self.lock()

    def _current_time_ms(self) -> int:
        """获取当前时间戳 (毫秒)。"""
        import time
        return int(time.time() * 1000)

    def notify(self, receiver, event):
        """
        重写 QApplication.notify，拦截所有事件以刷新空闲时间戳。

        任何用户交互事件 (鼠标、键盘、焦点变更) 都会重置空闲计时器。
        """
        from PyQt5.QtCore import QEvent

        # 刷新活动时间戳 (鼠标移动、按键、滚轮、焦点变更)
        if event.type() in (
            QEvent.MouseMove,
            QEvent.KeyPress,
            QEvent.Wheel,
            QEvent.FocusIn,
            QEvent.MouseButtonPress,
            QEvent.MouseButtonRelease,
        ):
            self._last_activity = self._current_time_ms()

        return super().notify(receiver, event)

    # ---------- 退出 ----------

    def quit(self):
        """安全退出应用: 清理数据库连接后退出。"""
        self._stop_idle_monitor()
        self.database.set_setting("locked", "1")
        self.database.close()
        super().quit()