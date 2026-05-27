"""
KeyCloset Hub - 笔记编辑器
Markdown 编辑 + HTML 预览 (分屏或切换模式)。

功能:
  - 纯文本编辑区，支持 Markdown 语法
  - 实时 HTML 预览 (使用 markdown 库 + Pygments 代码高亮)
  - 编辑/预览模式切换
  - 导出为 .md 文件
  - 标题 + 标签输入
"""

from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
)

from ..models import ItemModel
from ..utils import export_note
from .theme import COLORS


class NoteEditor(QDialog):
    """
    笔记编辑器对话框。

    支持两种模式:
      - 新建模式: item 为 None
      - 编辑模式: item 为已有条目实例

    Signals:
        item_saved: 保存成功后发射，携带更新后的 ItemModel
    """

    item_saved = pyqtSignal(ItemModel)

    def __init__(self, item: ItemModel = None, parent=None):
        super().__init__(parent)
        self._item = item
        self._is_new = item is None

        self.setWindowTitle("新增笔记" if self._is_new else "编辑笔记")
        self.setFixedSize(640, 520)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_window']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 8px;
            }}
        """)

        self._preview_mode = False
        self._setup_ui()

        if not self._is_new:
            self._load_item()

    def _setup_ui(self):
        """构建编辑器 UI。"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        # 标题行
        title_row = QHBoxLayout()
        title_label = QLabel("新增笔记" if self._is_new else "编辑笔记")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {COLORS['text_primary']};")
        title_row.addWidget(title_label)
        title_row.addStretch()

        # 编辑/预览切换按钮
        self.toggle_btn = QPushButton("预览")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: #F0F0F0;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #E5E5E5;
            }
        """)
        self.toggle_btn.clicked.connect(self._toggle_preview)
        title_row.addWidget(self.toggle_btn)
        main_layout.addLayout(title_row)

        # 笔记标题输入
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("笔记标题")
        self.title_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 1px solid #333333;
            }
        """)
        main_layout.addWidget(self.title_input)

        # Markdown 编辑区 / 预览区
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("在此输入 Markdown 内容...\n\n# 标题\n\n**粗体** *斜体*\n\n- 列表项")
        self.editor.setFont(QFont("Consolas", 11))
        self.editor.setStyleSheet("""
            QTextEdit {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border: 1px solid #333333;
            }
        """)

        self.preview = QTextBrowser()
        self.preview.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: #FFFFFF;
            }
        """)
        self.preview.hide()

        main_layout.addWidget(self.editor)
        main_layout.addWidget(self.preview)

        # 底部: 标签 + 导出按钮
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("标签 (逗号分隔)")
        self.tags_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #333333;
            }
        """)
        bottom_row.addWidget(self.tags_input)

        export_btn = QPushButton("导出 .md")
        export_btn.setStyleSheet("""
            QPushButton {
                background: #F0F0F0;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                padding: 6px 14px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #E5E5E5;
            }
        """)
        export_btn.clicked.connect(self._export_note)
        bottom_row.addWidget(export_btn)

        bottom_row.addStretch()

        # 取消/保存按钮
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
        bottom_row.addWidget(cancel_btn)

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
        bottom_row.addWidget(save_btn)

        main_layout.addLayout(bottom_row)

    def _toggle_preview(self):
        """切换编辑/预览模式。"""
        self._preview_mode = not self._preview_mode
        if self._preview_mode:
            # 切换到预览: 渲染 Markdown 为 HTML
            html = self._render_markdown(self.editor.toPlainText())
            self.preview.setHtml(html)
            self.editor.hide()
            self.preview.show()
            self.toggle_btn.setText("编辑")
        else:
            # 切换回编辑
            self.preview.hide()
            self.editor.show()
            self.toggle_btn.setText("预览")

    def _render_markdown(self, md_text: str) -> str:
        """
        将 Markdown 文本渲染为 HTML。

        使用 markdown 库，扩展 extra (表格、代码块等) 和 codehilite (Pygments 代码高亮)。
        """
        try:
            import markdown
            html = markdown.markdown(
                md_text,
                extensions=["extra", "codehilite", "fenced_code"],
            )
            # 基础样式注入
            styled_html = f"""
            <html><head><style>
                body {{
                    font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
                    font-size: 13px;
                    color: #1A1A1A;
                    line-height: 1.7;
                    padding: 12px;
                }}
                h1, h2, h3 {{ color: #1A1A1A; margin-top: 16px; }}
                code {{
                    background: #F5F5F5;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: "Consolas", monospace;
                    font-size: 11px;
                }}
                pre {{
                    background: #F5F5F5;
                    padding: 12px;
                    border-radius: 6px;
                    overflow-x: auto;
                }}
                pre code {{ background: transparent; padding: 0; }}
                blockquote {{
                    border-left: 3px solid #E0E0E0;
                    padding-left: 12px;
                    color: #666666;
                    margin-left: 0;
                }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{
                    border: 1px solid #E0E0E0;
                    padding: 8px 12px;
                    text-align: left;
                }}
                th {{ background: #F5F5F5; }}
                a {{ color: #333333; }}
            </style></head><body>{html}</body></html>
            """
            return styled_html
        except ImportError:
            # 如果 markdown 库不可用，显示纯文本
            return f"<pre style='font-family:Consolas; font-size:12px; padding:16px;'>{md_text}</pre>"

    def _export_note(self):
        """导出当前笔记为 .md 文件。"""
        title = self.title_input.text().strip() or "未命名笔记"
        content = self.editor.toPlainText()

        if not content:
            QMessageBox.information(self, "提示", "笔记内容为空，无法导出")
            return

        try:
            filepath = export_note(title, content)
            QMessageBox.information(self, "导出成功", f"笔记已导出到:\n{filepath}")
        except Exception as e:
            QMessageBox.warning(self, "导出失败", str(e))

    def _load_item(self):
        """编辑模式下加载已有数据。"""
        if self._item:
            self.title_input.setText(self._item.title)
            self.editor.setPlainText(self._item.content)
            self.tags_input.setText(", ".join(self._item.tags))

    def _on_save(self):
        """保存笔记条目。"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入笔记标题")
            return

        content = self.editor.toPlainText()

        # 解析标签
        tags_text = self.tags_input.text().strip()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()] if tags_text else []

        if self._is_new:
            item = ItemModel(
                category="note",
                title=title,
                content=content,
                tags=tags,
            )
        else:
            item = self._item
            item.title = title
            item.content = content
            item.tags = tags
            item.updated_at = datetime.now().isoformat()

        # 生成摘要 (内容前 50 字符)
        item.summary = content[:50].replace("\n", " ") if content else "空笔记"

        self.item_saved.emit(item)
        self.accept()