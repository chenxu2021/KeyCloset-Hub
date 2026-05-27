"""
KeyCloset Hub - 文档管理面板
支持拖拽或选择文件导入，存储到本地目录，记录元数据。

功能:
  - 拖拽文件到区域导入
  - 点击按钮选择文件导入
  - 用系统默认程序打开文件
  - 标题 + 标签输入
  - 导入文件自动复制到 ~/.keycloset/documents/ 并 UUID 重命名
"""

import os
from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from ..models import ItemModel
from ..utils import import_document
from .theme import COLORS


class DocumentImporter(QDialog):
    """
    文档导入对话框。

    支持两种方式导入:
      1. 点击"选择文件"按钮
      2. 直接拖拽文件到对话框区域

    Signals:
        item_saved: 导入成功时发射，携带 ItemModel
    """

    item_saved = pyqtSignal(ItemModel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_info = None  # (stored_path, file_size, file_type)

        self.setWindowTitle("导入文档")
        self.setFixedSize(460, 340)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAcceptDrops(True)  # 启用拖拽支持
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_window']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 8px;
            }}
        """)
        self._setup_ui()

    def _setup_ui(self):
        """构建导入对话框 UI。"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        # 标题
        title_label = QLabel("导入文档")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {COLORS['text_primary']};")
        main_layout.addWidget(title_label)

        # 拖拽区域
        self.drop_area = QLabel("将文件拖拽到此处\n或点击下方按钮选择")
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setMinimumHeight(120)
        self.drop_area.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {COLORS['border_input']};
                border-radius: 8px;
                background-color: {COLORS['bg_sidebar']};
                color: {COLORS['text_secondary']};
                font-size: 13px;
                padding: 24px;
            }}
        """)
        main_layout.addWidget(self.drop_area)

        # 选择文件按钮
        select_btn = QPushButton("选择文件...")
        select_btn.setStyleSheet("""
            QPushButton {
                background: #F0F0F0;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #E5E5E5;
            }
        """)
        select_btn.clicked.connect(self._select_file)
        main_layout.addWidget(select_btn, alignment=Qt.AlignCenter)

        # 已选文件信息
        self.file_info_label = QLabel("未选择文件")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        main_layout.addWidget(self.file_info_label)

        # 文档标题
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("文档标题 (默认使用文件名)")
        self.title_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #333333;
            }
        """)
        main_layout.addWidget(self.title_input)

        # 标签
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("标签 (逗号分隔)")
        self.tags_input.setStyleSheet(self.title_input.styleSheet())
        main_layout.addWidget(self.tags_input)

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

        self.save_btn = QPushButton("导入")
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #999999;
            }
        """)
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)

        main_layout.addLayout(button_layout)

    def _select_file(self):
        """打开系统文件对话框选择文件。"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "选择文档", "", "所有文件 (*.*)"
        )
        if filepath:
            self._process_file(filepath)

    def _process_file(self, filepath: str):
        """
        处理选中的文件: 复制到存储目录并显示信息。

        Args:
            filepath: 源文件路径
        """
        try:
            stored_path, file_size, file_type = import_document(filepath)

            self._file_info = (stored_path, file_size, file_type, filepath)

            # 更新 UI
            original_name = os.path.basename(filepath)
            self.file_info_label.setText(f"已选择: {original_name} ({self._format_size(file_size)})")
            self.drop_area.setStyleSheet(f"""
                QLabel {{
                    border: 2px solid {COLORS['accent']};
                    border-radius: 8px;
                    background-color: {COLORS['bg_sidebar']};
                    color: {COLORS['text_primary']};
                    font-size: 13px;
                    padding: 24px;
                }}
            """)
            self.drop_area.setText(f"✓ 文件已就绪\n{original_name}")

            # 自动填充标题
            if not self.title_input.text():
                name_without_ext = os.path.splitext(original_name)[0]
                self.title_input.setText(name_without_ext)

            self.save_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "导入失败", f"无法导入文件:\n{str(e)}")

    def _on_save(self):
        """完成文档导入。"""
        if not self._file_info:
            return

        stored_path, file_size, file_type, original_path = self._file_info
        title = self.title_input.text().strip() or os.path.basename(original_path)

        tags_text = self.tags_input.text().strip()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()] if tags_text else []

        item = ItemModel(
            category="document",
            title=title,
            file_path=original_path,
            stored_path=stored_path,
            file_size=file_size,
            file_type=file_type,
            tags=tags,
        )
        item.summary = item.format_summary()

        self.item_saved.emit(item)
        self.accept()

    # ---------- 拖拽事件处理 ----------

    def dragEnterEvent(self, event):
        """拖拽进入时检查是否为文件。"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet(f"""
                QLabel {{
                    border: 2px dashed {COLORS['accent']};
                    border-radius: 8px;
                    background-color: {COLORS['bg_hover']};
                    color: {COLORS['text_primary']};
                    font-size: 13px;
                    padding: 24px;
                }}
            """)

    def dragLeaveEvent(self, event):
        """拖拽离开时恢复样式。"""
        if not self._file_info:
            self.drop_area.setStyleSheet(f"""
                QLabel {{
                    border: 2px dashed {COLORS['border_input']};
                    border-radius: 8px;
                    background-color: {COLORS['bg_sidebar']};
                    color: {COLORS['text_secondary']};
                    font-size: 13px;
                    padding: 24px;
                }}
            """)

    def dropEvent(self, event):
        """接收拖放的文件。"""
        urls = event.mimeData().urls()
        if urls:
            filepath = urls[0].toLocalFile()
            if os.path.isfile(filepath):
                self._process_file(filepath)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小。"""
        for unit in ("B", "KB", "MB", "GB"):
            if size_bytes < 1024:
                return f"{size_bytes} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


def open_document_file(stored_path: str):
    """
    用系统默认程序打开文档文件。

    Args:
        stored_path: 文档本地存储路径
    """
    if not os.path.exists(stored_path):
        QMessageBox.warning(None, "文件不存在", f"文件已丢失:\n{stored_path}")
        return

    try:
        os.startfile(stored_path)
    except Exception as e:
        QMessageBox.warning(None, "打开失败", f"无法打开文件:\n{str(e)}")