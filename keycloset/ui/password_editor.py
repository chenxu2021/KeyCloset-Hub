"""
KeyCloset Hub - 密码条目编辑器
用于新增和编辑密码条目。

对话框包含字段:
  - 标题 (必填)
  - 网址 (URL)
  - 账号 (可复制)
  - 密码 (可复制, 可生成随机密码)
  - 备注 (多行文本)
  - 标签 (逗号分隔)
"""

import json
import secrets
import string

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..models import ItemModel
from .theme import COLORS


class PasswordEditor(QDialog):
    """
    密码条目编辑器对话框。

    支持两种模式:
      - 新建模式: item_model 为 None
      - 编辑模式: item_model 为已有条目实例
    """

    item_saved = pyqtSignal(ItemModel)

    def __init__(self, item: ItemModel = None, parent=None):
        super().__init__(parent)
        self._item = item
        self._is_new = item is None

        self.setWindowTitle("新增密码" if self._is_new else "编辑密码")
        self.setFixedSize(480, 480)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_window']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 8px;
            }}
        """)
        self._setup_ui()

        if not self._is_new:
            self._load_item()

    def _setup_ui(self):
        """构建编辑器 UI。"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        # 标题
        title_label = QLabel("新增密码" if self._is_new else "编辑密码")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {COLORS['text_primary']};")
        main_layout.addWidget(title_label)

        # 表单区域
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        input_style = """
            QLineEdit {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #333333;
            }
        """

        # 标题
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("例如: GitHub")
        self.title_input.setStyleSheet(input_style)
        form_layout.addRow("标题:", self.title_input)

        # 网址
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://github.com")
        self.url_input.setStyleSheet(input_style)
        form_layout.addRow("网址:", self.url_input)

        # 账号
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("yourname@example.com")
        self.account_input.setStyleSheet(input_style)
        form_layout.addRow("账号:", self.account_input)

        # 密码 + 生成按钮
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("输入或生成密码")
        self.password_input.setStyleSheet(input_style)
        password_layout.addWidget(self.password_input)

        # 显示/隐藏密码切换
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedWidth(36)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background: #F0F0F0;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                font-size: 14px;
                padding: 4px;
            }
            QPushButton:hover {
                background: #E5E5E5;
            }
        """)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.toggled.connect(self._toggle_password_visibility)
        password_layout.addWidget(self.show_password_btn)

        # 生成随机密码按钮
        gen_password_btn = QPushButton("生成")
        gen_password_btn.setStyleSheet("""
            QPushButton {
                background: #F0F0F0;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #E5E5E5;
            }
        """)
        gen_password_btn.clicked.connect(self._generate_password)
        password_layout.addWidget(gen_password_btn)

        form_layout.addRow("密码:", password_layout)

        # 备注
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("备注信息 (可选)")
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 1px solid #333333;
            }
        """)
        form_layout.addRow("备注:", self.notes_input)

        # 标签
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("work, personal (逗号分隔)")
        self.tags_input.setStyleSheet(input_style)
        form_layout.addRow("标签:", self.tags_input)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
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
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
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
        """)
        save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(save_btn)

        main_layout.addLayout(button_layout)

    def _toggle_password_visibility(self, checked: bool):
        """切换密码可见性。"""
        self.password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

    def _generate_password(self):
        """生成 16 位随机强密码。"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(alphabet) for _ in range(16))
        self.password_input.setText(password)
        # 生成密码时自动显示
        self.password_input.setEchoMode(QLineEdit.Normal)
        self.show_password_btn.setChecked(True)

    def _load_item(self):
        """编辑模式下加载已有数据到表单。"""
        if self._item:
            self.title_input.setText(self._item.title)
            self.url_input.setText(self._item.url)
            self.account_input.setText(self._item.account)
            self.password_input.setText(self._item.password)
            self.notes_input.setPlainText(self._item.notes)
            self.tags_input.setText(", ".join(self._item.tags))

    def _on_save(self):
        """保存条目数据。"""
        # 验证必填字段
        title = self.title_input.text().strip()
        if not title:
            self._show_error("请输入标题")
            return

        # 解析标签
        tags_text = self.tags_input.text().strip()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()] if tags_text else []

        # 构建 ItemModel
        from datetime import datetime

        if self._is_new:
            item = ItemModel(
                category="password",
                title=title,
                url=self.url_input.text().strip(),
                account=self.account_input.text().strip(),
                password=self.password_input.text(),
                notes=self.notes_input.toPlainText().strip(),
                tags=tags,
            )
        else:
            item = self._item
            item.title = title
            item.url = self.url_input.text().strip()
            item.account = self.account_input.text().strip()
            item.password = self.password_input.text()
            item.notes = self.notes_input.toPlainText().strip()
            item.tags = tags
            item.updated_at = datetime.now().isoformat()

        # 生成摘要
        item.summary = item.format_summary()

        self.item_saved.emit(item)
        self.accept()

    def _show_error(self, message: str):
        """显示错误提示。"""
        QMessageBox.warning(self, "提示", message)

    def _center_on_parent(self):
        """对话框居中于父窗口。"""
        if self.parent():
            parent_geo = self.parent().geometry()
            size = self.geometry()
            x = parent_geo.x() + (parent_geo.width() - size.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - size.height()) // 2
            self.move(x, y)