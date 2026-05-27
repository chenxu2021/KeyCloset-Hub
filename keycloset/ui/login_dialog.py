"""
KeyCloset Hub - 登录/解锁对话框
首次使用时设置主密码，后续启动时验证主密码解锁。

UI 设计:
  - 居中模态对话框，简洁的居中表单
  - 密码输入框支持眼睛图标切换可见性
  - 错误提示使用浅灰文字，不喧宾夺主
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..crypto import create_verification_data, verify_master_password
from ..database import Database


class LoginDialog(QDialog):
    """
    解锁/设置主密码对话框。

    根据数据库中是否已有 salt 自动切换模式:
      - 首次使用: "设置主密码" 模式 (需确认密码)
      - 后续启动: "解锁" 模式 (仅输入密码)

    Signals:
        unlock_success: 解锁成功后发射，携带主密码字符串
    """

    unlock_success = pyqtSignal(str)

    def __init__(self, database: Database, parent=None):
        super().__init__(parent)
        self.database = database
        self._is_first_time = not self._has_existing_master_password()

        self._setup_ui()
        self._center_on_screen()

    def _has_existing_master_password(self) -> bool:
        """检查数据库中是否已存在 salt (即是否已设置过主密码)。"""
        return bool(self.database.get_setting("salt"))

    def _setup_ui(self):
        """构建对话框 UI。"""
        # 窗口基础设置
        self.setWindowTitle("KeyCloset Hub" if self._is_first_time else "解锁 KeyCloset Hub")
        self.setFixedSize(380, 320 if self._is_first_time else 260)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(16)

        # 标题
        title_label = QLabel("KeyCloset Hub")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 16))
        title_label.setStyleSheet("color: #1A1A1A; font-weight: 600;")
        layout.addWidget(title_label)

        # 副标题
        subtitle_text = "设置您的主密码以保护数据" if self._is_first_time else "请输入主密码解锁"
        subtitle_label = QLabel(subtitle_text)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #999999; font-size: 12px;")
        layout.addWidget(subtitle_label)

        layout.addSpacing(8)

        # 密码输入框
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("主密码")
        self.password_input.setMinimumHeight(36)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDDDDD;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #333333;
            }
        """)
        layout.addWidget(self.password_input)

        # 确认密码输入框 (仅首次设置时显示)
        if self._is_first_time:
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)
            self.confirm_input.setPlaceholderText("确认主密码")
            self.confirm_input.setMinimumHeight(36)
            self.confirm_input.setStyleSheet(self.password_input.styleSheet())
            layout.addWidget(self.confirm_input)

        # 错误提示标签
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #888888; font-size: 11px;")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFlat(True)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #999999;
                border: none;
                padding: 8px 20px;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #1A1A1A;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.submit_btn = QPushButton("设置主密码" if self._is_first_time else "解锁")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        self.submit_btn.clicked.connect(self._on_submit)
        self.submit_btn.setDefault(True)
        button_layout.addWidget(self.submit_btn)

        layout.addLayout(button_layout)

        # 绑定回车键
        self.password_input.returnPressed.connect(self._on_submit)
        if self._is_first_time:
            self.confirm_input.returnPressed.connect(self._on_submit)

    def _center_on_screen(self):
        """将对话框居中于屏幕。"""
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def _on_submit(self):
        """处理提交按钮点击。"""
        password = self.password_input.text()

        # 密码不能为空
        if not password:
            self._show_error("密码不能为空")
            return

        if self._is_first_time:
            # 首次设置模式: 需确认密码一致
            confirm = self.confirm_input.text()
            if not confirm:
                self._show_error("请确认主密码")
                return
            if password != confirm:
                self._show_error("两次输入的密码不一致")
                return
            if len(password) < 4:
                self._show_error("主密码长度至少为 4 位")
                return

            # 创建加密验证数据并持久化
            salt_hex, encrypted_phrase = create_verification_data(password)
            self.database.set_setting("salt", salt_hex)
            self.database.set_setting("verification", encrypted_phrase)
            self.database.set_setting("locked", "0")

            self.unlock_success.emit(password)
            self.accept()
        else:
            # 解锁模式: 验证密码
            salt_hex = self.database.get_setting("salt")
            encrypted_phrase = self.database.get_setting("verification")

            if verify_master_password(password, salt_hex, encrypted_phrase):
                self.database.set_setting("locked", "0")
                self.unlock_success.emit(password)
                self.accept()
            else:
                self._show_error("密码错误，请重试")
                self.password_input.selectAll()

    def _show_error(self, message: str):
        """显示错误提示信息。"""
        self.error_label.setText(message)
        self.error_label.setStyleSheet("color: #888888; font-size: 11px;")
        self.password_input.setFocus()

    def reject(self):
        """取消/关闭对话框 = 退出应用。"""
        super().reject()
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().quit()