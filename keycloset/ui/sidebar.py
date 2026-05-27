"""
KeyCloset Hub - 侧边栏组件
左侧导航面板，包含分类列表和标签列表。

视觉层次:
  - 分类列表 (password / note / document / favorite) 为固定导航项
  - 标签列表动态生成，从数据库中汇聚所有标签
  - 选中项以浅灰背景高亮，无彩色
  - 悬停时有微妙反馈
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..models import CATEGORIES
from .theme import COLORS, SIDEBAR_STYLESHEET


class Sidebar(QWidget):
    """
    侧边栏 — 左侧导航。

    Signals:
        category_changed: 用户点击分类时发射，携带分类 key 字符串
        tag_selected: 用户点击标签时发射，携带标签字符串
    """

    category_changed = pyqtSignal(str)
    tag_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet(f"background-color: {COLORS['bg_sidebar']};")
        self._setup_ui()

    def _setup_ui(self):
        """构建侧边栏 UI。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(0)

        # ---- 分类列表 ----
        self.category_list = QListWidget()
        self.category_list.setStyleSheet(SIDEBAR_STYLESHEET)
        self.category_list.setSpacing(0)

        for cat in CATEGORIES:
            item = QListWidgetItem(f"  {cat['icon']}  {cat['label']}")
            item.setData(1, cat["key"])  # 在 item data 中存储 key
            self.category_list.addItem(item)

        self.category_list.setCurrentRow(0)  # 默认选中"密码"
        self.category_list.currentRowChanged.connect(self._on_category_changed)
        layout.addWidget(self.category_list)

        # ---- 分割线 ----
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {COLORS['border_light']}; margin: 8px 16px;")
        layout.addWidget(separator)

        # ---- 标签区域标题 ----
        tag_header = QLabel("  标签")
        tag_header.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 11px;
            font-weight: 500;
            padding: 4px 16px;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(tag_header)

        # ---- 标签列表 ----
        self.tag_list = QListWidget()
        self.tag_list.setStyleSheet(SIDEBAR_STYLESHEET)
        self.tag_list.setSpacing(0)
        self.tag_list.itemClicked.connect(self._on_tag_clicked)
        layout.addWidget(self.tag_list)

        # 标签列表占剩余空间
        layout.setStretch(0, 0)  # 分类列表不拉伸
        layout.setStretch(3, 1)  # 标签列表可拉伸

    def _on_category_changed(self, index: int):
        """用户切换分类时发射信号。"""
        if 0 <= index < len(CATEGORIES):
            key = CATEGORIES[index]["key"]
            self.category_changed.emit(key)

    def _on_tag_clicked(self, item: QListWidgetItem):
        """用户点击标签时发射信号。"""
        tag = item.data(1)
        if tag:
            self.tag_selected.emit(tag)

    def update_tags(self, tags: list):
        """
        从外部更新标签列表。

        Args:
            tags: 标签字符串列表
        """
        self.tag_list.clear()

        if not tags:
            # 无标签时显示占位文本
            placeholder = QListWidgetItem("  暂无标签")
            placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsSelectable)
            placeholder.setData(1, "")
            self.tag_list.addItem(placeholder)
            return

        for tag in tags:
            item = QListWidgetItem(f"  {tag}")
            item.setData(1, tag)
            self.tag_list.addItem(item)

    def get_current_category(self) -> str:
        """
        获取当前选中的分类 key。

        Returns:
            str: 分类 key (password/note/document/favorite)
        """
        current = self.category_list.currentRow()
        if 0 <= current < len(CATEGORIES):
            return CATEGORIES[current]["key"]
        return "password"

    def select_category(self, key: str):
        """
        程序化选中指定分类。

        Args:
            key: 分类 key
        """
        for i, cat in enumerate(CATEGORIES):
            if cat["key"] == key:
                self.category_list.setCurrentRow(i)
                break