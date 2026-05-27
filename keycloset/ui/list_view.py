"""
KeyCloset Hub - 列表视图组件
右侧主内容区域，展示当前分类下的条目列表。

设计要点:
  - 每项两行: 标题行 + 摘要行
  - 摘要行显示分类相关辅助信息 (域名、时间、文件大小等)
  - 操作按钮 (复制账号/密码、收藏、编辑、删除) 鼠标悬停时浮出
  - 空状态时显示友好的占位提示
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..models import ItemModel
from ..utils import format_relative_time
from .theme import COLORS, LIST_ITEM_STYLESHEET


class ItemListWidget(QListWidget):
    """
    自定义列表控件，重写以支持悬停时显示操作按钮。
    """

    item_double_clicked = pyqtSignal(ItemModel)
    item_copy_password = pyqtSignal(ItemModel)
    item_copy_account = pyqtSignal(ItemModel)
    item_edit = pyqtSignal(ItemModel)
    item_delete = pyqtSignal(ItemModel)
    item_toggle_favorite = pyqtSignal(ItemModel)
    item_open_file = pyqtSignal(ItemModel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(LIST_ITEM_STYLESHEET)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setMouseTracking(True)
        self.setSpacing(0)

        # 存储 item_id -> ItemModel 的映射
        self._item_models: dict = {}

        self.itemClicked.connect(self._on_item_clicked)
        self.setContextMenuPolicy(Qt.NoContextMenu)

    def _on_item_clicked(self, list_item: QListWidgetItem):
        """点击条目时触发双击信号 (单机选取，双击编辑)。"""
        item_model = self._get_model_from_item(list_item)
        if item_model:
            self.item_double_clicked.emit(item_model)

    def _get_model_from_item(self, list_item: QListWidgetItem) -> ItemModel:
        """从 QListWidgetItem 的 data 中取回 ItemModel。"""
        item_id = list_item.data(1)
        return self._item_models.get(item_id)

    def load_items(self, items: list, fernet=None):
        """
        加载条目列表。

        Args:
            items: ItemModel 列表
            fernet: Fernet 实例 (用于解密操作时使用)
        """
        self.clear()
        self._item_models.clear()

        for item in items:
            if item.id is None:
                continue
            self._item_models[item.id] = item

            # 创建自定义条目 widget
            item_widget = _ItemRowWidget(item)
            item_widget.copy_password_clicked.connect(
                lambda checked, m=item: self.item_copy_password.emit(m)
            )
            item_widget.copy_account_clicked.connect(
                lambda checked, m=item: self.item_copy_account.emit(m)
            )
            item_widget.edit_clicked.connect(
                lambda checked, m=item: self.item_edit.emit(m)
            )
            item_widget.delete_clicked.connect(
                lambda checked, m=item: self.item_delete.emit(m)
            )
            item_widget.favorite_clicked.connect(
                lambda checked, m=item: self.item_toggle_favorite.emit(m)
            )
            item_widget.open_clicked.connect(
                lambda checked, m=item: self.item_open_file.emit(m)
            )

            list_item = QListWidgetItem()
            list_item.setData(1, item.id)
            list_item.setSizeHint(item_widget.sizeHint())
            self.addItem(list_item)
            self.setItemWidget(list_item, item_widget)

    def remove_item_by_id(self, item_id: int):
        """根据 ID 移除列表中的条目。"""
        self._item_models.pop(item_id, None)
        for i in range(self.count()):
            item = self.item(i)
            if item and item.data(1) == item_id:
                self.takeItem(i)
                break


class _ItemRowWidget(QWidget):
    """
    单行条目组件 — 两行文本 + 悬停操作按钮。

    内部布局:
      ┌──────────────────────────────────────────┐
      │  标题 (bold, #1A1A1A)                     │
      │  摘要 (small, #999999)     [操作按钮区域]  │
      └──────────────────────────────────────────┘
    """

    copy_password_clicked = pyqtSignal()
    copy_account_clicked = pyqtSignal()
    edit_clicked = pyqtSignal()
    delete_clicked = pyqtSignal()
    favorite_clicked = pyqtSignal()
    open_clicked = pyqtSignal()

    def __init__(self, item: ItemModel, parent=None):
        super().__init__(parent)
        self.item = item
        self._buttons_visible = False
        self._setup_ui()
        self.setMouseTracking(True)

    def _setup_ui(self):
        """构建条目 UI。"""
        self.setFixedHeight(56)
        self.setStyleSheet(f"background-color: {COLORS['bg_window']};")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 8, 8, 8)
        main_layout.setSpacing(8)

        # ---- 左侧文本区域 ----
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        # 标题
        self.title_label = QLabel(self.item.title or "无标题")
        self.title_label.setFont(QFont("Segoe UI", 12))
        self.title_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")

        # 摘要
        summary_text = self.item.summary or self.item.format_summary()
        # 添加时间
        time_str = format_relative_time(self.item.updated_at)
        if time_str:
            summary_text = f"{summary_text} · {time_str}" if summary_text else time_str

        self.summary_label = QLabel(summary_text)
        self.summary_label.setFont(QFont("Segoe UI", 10))
        self.summary_label.setStyleSheet(f"color: {COLORS['text_secondary']};")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.summary_label)
        main_layout.addLayout(text_layout)

        # 弹性空间
        main_layout.addStretch()

        # ---- 操作按钮区域 (默认隐藏) ----
        self.button_container = QWidget()
        self.button_container.setFixedHeight(32)
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(4)

        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                color: #666666;
                min-width: 32px;
            }
            QPushButton:hover {
                background-color: #EEEEEE;
                color: #1A1A1A;
            }
        """

        # 密码模块: 复制账号、复制密码按钮
        if self.item.category == "password":
            self.copy_account_btn = QPushButton("账号")
            self.copy_account_btn.setStyleSheet(button_style)
            self.copy_account_btn.clicked.connect(self.copy_account_clicked.emit)
            self.copy_account_btn.setToolTip("复制账号")
            button_layout.addWidget(self.copy_account_btn)

            self.copy_password_btn = QPushButton("密码")
            self.copy_password_btn.setStyleSheet(button_style)
            self.copy_password_btn.clicked.connect(self.copy_password_clicked.emit)
            self.copy_password_btn.setToolTip("复制密码")
            button_layout.addWidget(self.copy_password_btn)

        # 笔记模块: 导出按钮
        if self.item.category == "note":
            self.export_btn = QPushButton("导出")
            self.export_btn.setStyleSheet(button_style)
            self.export_btn.clicked.connect(self.copy_password_clicked.emit)  # 复用信号
            self.export_btn.setToolTip("导出 Markdown")
            button_layout.addWidget(self.export_btn)

        # 文档模块: 打开文件按钮
        if self.item.category == "document":
            self.open_btn = QPushButton("打开")
            self.open_btn.setStyleSheet(button_style)
            self.open_btn.clicked.connect(self.open_clicked.emit)
            self.open_btn.setToolTip("用系统程序打开文件")
            button_layout.addWidget(self.open_btn)

        # 通用操作按钮
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.setStyleSheet(button_style)
        self.edit_btn.clicked.connect(self.edit_clicked.emit)
        self.edit_btn.setToolTip("编辑条目")
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.setStyleSheet(button_style)
        self.delete_btn.clicked.connect(self.delete_clicked.emit)
        self.delete_btn.setToolTip("删除条目")
        button_layout.addWidget(self.delete_btn)

        # 收藏星标按钮
        fav_text = "★" if self.item.is_favorite else "☆"
        self.fav_btn = QPushButton(fav_text)
        self.fav_btn.setStyleSheet(button_style + """
            QPushButton {
                font-size: 14px;
            }
        """)
        self.fav_btn.clicked.connect(self.favorite_clicked.emit)
        self.fav_btn.setToolTip("切换收藏")
        button_layout.addWidget(self.fav_btn)

        self.button_container.hide()  # 默认隐藏
        main_layout.addWidget(self.button_container)

    def enterEvent(self, event):
        """鼠标进入时显示操作按钮。"""
        self._buttons_visible = True
        self.button_container.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开时隐藏操作按钮。"""
        self._buttons_visible = False
        self.button_container.hide()
        super().leaveEvent(event)