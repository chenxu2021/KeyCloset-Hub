"""
KeyCloset Hub - 全局搜索栏组件
位于标题栏中，支持 Ctrl+F 快捷键聚焦。

设计:
  - 圆角灰底输入框，左侧 🔍 图标
  - 实时搜索 (输入即搜)
  - placeholder 文字 "搜索标题、标签..."
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget

from .theme import SEARCH_BAR_STYLESHEET


class SearchBar(QWidget):
    """
    全局搜索栏组件。

    Signals:
        search_changed: 搜索文本变化时发射，携带当前搜索关键词
    """

    search_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """构建搜索栏 UI。"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索标题、标签...")
        self.search_input.setStyleSheet(SEARCH_BAR_STYLESHEET)
        self.search_input.setFont(QFont("Segoe UI", 12))
        self.search_input.textChanged.connect(self.search_changed.emit)

        layout.addWidget(self.search_input)

        self.setFixedWidth(280)

    def get_text(self) -> str:
        """获取当前搜索文本。"""
        return self.search_input.text().strip()

    def clear(self):
        """清空搜索框。"""
        self.search_input.clear()

    def focus_search(self):
        """聚焦并选中全部文本，供快捷键调用。"""
        self.search_input.setFocus()
        self.search_input.selectAll()