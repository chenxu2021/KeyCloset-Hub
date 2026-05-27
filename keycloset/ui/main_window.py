"""
KeyCloset Hub - 主窗口
无边框主窗口，整合侧边栏、列表视图、搜索栏、状态栏。

核心职责:
  1. 连接所有 UI 组件与业务逻辑
  2. 处理加密/解密流程 (密码条目及笔记内容)
  3. 管理键盘快捷键
  4. 协调各模块间的数据流
"""

import json

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QShortcut,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ..crypto import decrypt_data, encrypt_data
from ..database import Database
from ..models import ItemModel
from ..utils import format_relative_time, export_note
from .document_view import DocumentImporter, open_document_file
from .list_view import ItemListWidget
from .login_dialog import LoginDialog
from .note_editor import NoteEditor
from .password_editor import PasswordEditor
from .search_bar import SearchBar
from .sidebar import Sidebar
from .theme import COLORS, DIMENSIONS, GLOBAL_STYLESHEET


class MainWindow(QMainWindow):
    """
    KeyCloset Hub 主窗口。

    生命周期:
      1. 构造时初始化数据库和加密层
      2. 弹出 LoginDialog 验证主密码
      3. 验证通过后加载 UI 和数据
      4. 运行中处理用户操作和加解密
      5. 锁定时清除内存中的敏感数据
    """

    def __init__(self, database: Database, master_password: str, lock_callback):
        super().__init__()
        self.database = database
        self.master_password = master_password
        self._lock_callback = lock_callback  # 锁定回调，由 app.py 提供

        # 初始化 Fernet 加密实例
        salt_hex = self.database.get_setting("salt")
        from ..crypto import get_fernet
        self._fernet = get_fernet(master_password, salt_hex)

        # 当前状态
        self._current_category = "password"
        self._search_query = ""

        self._setup_window()
        self._setup_shortcuts()
        self._apply_stylesheet()
        self._refresh_content()

    def _setup_window(self):
        """初始化主窗口 UI 布局。"""
        self.setWindowTitle("KeyCloset Hub")
        self.setMinimumSize(DIMENSIONS["window_min_width"], DIMENSIONS["window_min_height"])
        self.resize(DIMENSIONS["window_width"], DIMENSIONS["window_height"])

        # 无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # 中央组件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- 自定义标题栏 ----
        main_layout.addWidget(self._create_titlebar())

        # ---- 主体区域: 侧边栏 + 分割线 + 内容 ----
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # 侧边栏
        self.sidebar = Sidebar()
        self.sidebar.category_changed.connect(self._on_category_changed)
        self.sidebar.tag_selected.connect(self._on_tag_selected)
        body_layout.addWidget(self.sidebar)

        # 分割线
        divider = QWidget()
        divider.setFixedWidth(1)
        divider.setStyleSheet(f"background-color: {COLORS['border_light']};")
        body_layout.addWidget(divider)

        # 右侧内容区域
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 内容区域顶部的搜索栏 (与侧边栏平级但在右侧顶部)
        search_container = QWidget()
        search_container.setFixedHeight(44)
        search_container.setStyleSheet(f"background-color: {COLORS['bg_titlebar']};")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(16, 8, 16, 8)

        # 分类标题
        self.category_title = QLabel("密码")
        self.category_title.setFont(QFont("Segoe UI", 14))
        self.category_title.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        search_layout.addWidget(self.category_title)
        search_layout.addStretch()

        # 搜索栏
        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self._on_search_changed)
        search_layout.addWidget(self.search_bar)

        content_layout.addWidget(search_container)

        # 列表视图
        self.list_view = ItemListWidget()
        self.list_view.item_copy_password.connect(self._on_copy_password)
        self.list_view.item_copy_account.connect(self._on_copy_account)
        self.list_view.item_edit.connect(self._on_edit_item)
        self.list_view.item_delete.connect(self._on_delete_item)
        self.list_view.item_toggle_favorite.connect(self._on_toggle_favorite)
        self.list_view.item_open_file.connect(self._on_open_document)
        content_layout.addWidget(self.list_view)

        body_layout.addWidget(content)

        main_layout.addWidget(body)

        # ---- 状态栏 ----
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(DIMENSIONS["statusbar_height"])
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORS['bg_titlebar']};
                border-top: 1px solid {COLORS['border_light']};
                font-size: 11px;
                color: {COLORS['text_secondary']};
            }}
        """)
        self.status_label = QLabel("")
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(QLabel("Ctrl+N 新增  Ctrl+E 编辑  Ctrl+C 复制  Ctrl+L 锁定"))
        main_layout.addWidget(self.status_bar)

        self._update_status_bar()

    def _create_titlebar(self) -> QWidget:
        """创建自定义无边框标题栏。"""
        titlebar = QWidget()
        titlebar.setFixedHeight(DIMENSIONS["titlebar_height"])
        titlebar.setStyleSheet(f"background-color: {COLORS['bg_titlebar']};")
        titlebar.mousePressEvent = self._titlebar_mouse_press
        titlebar.mouseMoveEvent = self._titlebar_mouse_move
        titlebar.mouseDoubleClickEvent = self._titlebar_double_click

        layout = QHBoxLayout(titlebar)
        layout.setContentsMargins(12, 0, 4, 0)
        layout.setSpacing(0)

        # 应用图标和标题
        app_label = QLabel("⚿  KeyCloset Hub")
        app_label.setFont(QFont("Segoe UI", 11))
        app_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
        layout.addWidget(app_label)
        layout.addStretch()

        # 窗口控制按钮
        btn_style = """
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 14px;
                color: #666666;
                min-width: 32px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                color: #1A1A1A;
            }
        """

        minimize_btn = QPushButton("−")
        minimize_btn.setStyleSheet(btn_style)
        minimize_btn.clicked.connect(self.showMinimized)
        layout.addWidget(minimize_btn)

        maximize_btn = QPushButton("□")
        maximize_btn.setStyleSheet(btn_style)
        maximize_btn.clicked.connect(self._toggle_maximize)
        layout.addWidget(maximize_btn)

        close_btn = QPushButton("✕")
        close_btn.setStyleSheet(btn_style + """
            QPushButton:hover {
                background-color: #E0E0E0;
                color: #1A1A1A;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self._drag_pos = None
        return titlebar

    # ---------- 无边框窗口拖动 ----------

    def _titlebar_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()

    def _titlebar_mouse_move(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPos()

    def _titlebar_double_click(self, event):
        self._toggle_maximize()

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # ---------- 样式 ----------

    def _apply_stylesheet(self):
        """应用全局样式表。"""
        self.setStyleSheet(GLOBAL_STYLESHEET)

    # ---------- 快捷键 ----------

    def _setup_shortcuts(self):
        """注册全局键盘快捷键。"""
        # Ctrl+F — 聚焦搜索
        QShortcut(QKeySequence("Ctrl+F"), self, self._handle_search_focus)
        # Ctrl+N — 新增当前分类条目
        QShortcut(QKeySequence("Ctrl+N"), self, self._handle_new_item)
        # Ctrl+E — 编辑选中条目
        QShortcut(QKeySequence("Ctrl+E"), self, self._handle_edit_current)
        # Ctrl+C — 复制密码或相关项内容
        QShortcut(QKeySequence("Ctrl+C"), self, self._handle_copy)
        # Ctrl+L — 锁定应用
        QShortcut(QKeySequence("Ctrl+L"), self, self._handle_lock)
        # Escape — 清空搜索
        QShortcut(QKeySequence("Escape"), self, self._handle_escape)

    def _handle_search_focus(self):
        self.search_bar.focus_search()

    def _handle_new_item(self):
        self._on_new_item()

    def _handle_edit_current(self):
        current_item = self.list_view.currentItem()
        if current_item:
            item_model = self.list_view._get_model_from_item(current_item)
            if item_model:
                self._on_edit_item(item_model)

    def _handle_copy(self):
        current_item = self.list_view.currentItem()
        if current_item:
            item_model = self.list_view._get_model_from_item(current_item)
            if item_model:
                if item_model.category == "password":
                    self._on_copy_password(item_model)
                elif item_model.category == "note":
                    self._copy_to_clipboard(item_model.content)
                else:
                    self._copy_to_clipboard(item_model.title)

    def _handle_lock(self):
        if self._lock_callback:
            self._lock_callback()

    def _handle_escape(self):
        if self.search_bar.get_text():
            self.search_bar.clear()
        else:
            self.list_view.clearSelection()

    # ---------- 内容刷新 ----------

    def _refresh_content(self):
        """刷新列表视图和侧边栏标签。"""
        # 更新分类标题
        category_labels = {
            "password": "密码",
            "note": "笔记",
            "document": "文档",
            "favorite": "收藏",
        }
        self.category_title.setText(category_labels.get(self._current_category, "全部"))

        # 获取条目
        items = self.database.get_items(
            category=self._current_category,
            search_query=self._search_query,
        )

        # 解密敏感字段
        for item in items:
            self._decrypt_item(item)

        # 加载到列表
        self.list_view.load_items(items)

        # 更新侧边栏标签
        tags = self.database.get_all_tags()
        self.sidebar.update_tags(tags)

        # 更新状态栏
        self._update_status_bar()

    def _decrypt_item(self, item: ItemModel):
        """
        解密条目的加密字段并填入 ItemModel 的属性中。

        数据库中的 data_encrypted 和 content_encrypted 是加密存储的，
        此方法将它们解密后赋值给 ItemModel 的明文属性。
        """
        if not self._fernet:
            return

        # 获取数据库中的原始加密数据行
        row = None
        if item.id is not None:
            row = self.database.conn.execute(
                "SELECT data_encrypted, content_encrypted FROM items WHERE id = ?",
                (item.id,),
            ).fetchone()

        if row:
            if item.category == "password":
                encrypted_data = row["data_encrypted"]
                if encrypted_data:
                    decrypted_json = decrypt_data(self._fernet, encrypted_data)
                    if decrypted_json:
                        try:
                            data = json.loads(decrypted_json)
                            item.url = data.get("url", "")
                            item.account = data.get("account", "")
                            item.password = data.get("password", "")
                            item.notes = data.get("notes", "")
                        except json.JSONDecodeError:
                            pass

            elif item.category == "note":
                encrypted_content = row["content_encrypted"]
                if encrypted_content:
                    item.content = decrypt_data(self._fernet, encrypted_content)

    # ---------- 保存与加密 ----------

    def _save_password_item(self, item: ItemModel):
        """
        保存密码条目到数据库 (加密后写入)。

        流程:
          新建 → add_item 获取 ID → 加密 data_encrypted → update_item
          编辑 → 加密 data_encrypted → update_item
        """
        # 加密敏感字段
        sensitive_data = item.to_dict()  # url, account, password, notes
        encrypted = encrypt_data(self._fernet, json.dumps(sensitive_data, ensure_ascii=False))

        if item.id is None:
            # 新建
            item_id = self.database.add_item(item)
            item.id = item_id

        # 更新加密字段 (附加属性 _data_encrypted 传递给 update_item)
        item._data_encrypted = encrypted
        item.updated_at = __import__("datetime").datetime.now().isoformat()
        self.database.update_item(item)

    def _save_note_item(self, item: ItemModel):
        """
        保存笔记条目到数据库 (加密后写入)。
        """
        encrypted = encrypt_data(self._fernet, item.content)

        if item.id is None:
            item_id = self.database.add_item(item)
            item.id = item_id

        item._content_encrypted = encrypted
        item.updated_at = __import__("datetime").datetime.now().isoformat()
        self.database.update_item(item)

    def _save_document_item(self, item: ItemModel):
        """
        保存文档条目到数据库 (元数据明文，无加密内容)。
        """
        if item.id is None:
            item_id = self.database.add_item(item)
            item.id = item_id
        else:
            item._data_encrypted = ""
            item._content_encrypted = ""
            item.updated_at = __import__("datetime").datetime.now().isoformat()
            self.database.update_item(item)

    # ---------- 信号处理 ----------

    def _on_category_changed(self, category: str):
        """侧边栏分类切换。"""
        self._current_category = category
        self.search_bar.clear()
        self._search_query = ""
        self._refresh_content()

    def _on_tag_selected(self, tag: str):
        """侧边栏标签点击 — 在搜索框中设置标签关键词。"""
        self.search_bar.search_input.setText(tag)
        self._search_query = tag
        self._refresh_content()

    def _on_search_changed(self, query: str):
        """搜索框文本变化。"""
        self._search_query = query.strip()
        self._refresh_content()

    def _on_new_item(self):
        """新增当前分类条目。"""
        category = self._current_category
        if category == "favorite":
            category = "password"  # 收藏不是可新建的分类，默认新建密码

        if category == "password":
            dialog = PasswordEditor(parent=self)
            dialog.item_saved.connect(self._on_password_saved)
        elif category == "note":
            dialog = NoteEditor(parent=self)
            dialog.item_saved.connect(self._on_note_saved)
        elif category == "document":
            dialog = DocumentImporter(parent=self)
            dialog.item_saved.connect(self._on_document_saved)
        else:
            return

        self._center_dialog(dialog)
        dialog.exec_()

    def _on_edit_item(self, item: ItemModel):
        """编辑选中条目。"""
        if item.category == "password":
            editor = PasswordEditor(item=item, parent=self)
            editor.item_saved.connect(self._on_password_saved)
            self._center_dialog(editor)
            editor.exec_()
        elif item.category == "note":
            editor = NoteEditor(item=item, parent=self)
            editor.item_saved.connect(self._on_note_saved)
            self._center_dialog(editor)
            editor.exec_()
        elif item.category == "document":
            # 文档不可编辑内容，仅切换收藏
            pass

    def _on_password_saved(self, item: ItemModel):
        """密码编辑器保存后的回调。"""
        self._save_password_item(item)
        self._refresh_content()

    def _on_note_saved(self, item: ItemModel):
        """笔记编辑器保存后的回调。"""
        self._save_note_item(item)
        self._refresh_content()

    def _on_document_saved(self, item: ItemModel):
        """文档导入完成后的回调。"""
        self._save_document_item(item)
        self._refresh_content()

    def _on_delete_item(self, item: ItemModel):
        """删除条目。"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除 \"{item.title}\" 吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.database.delete_item(item.id)
            self._refresh_content()

    def _on_toggle_favorite(self, item: ItemModel):
        """切换收藏状态。"""
        item.is_favorite = not item.is_favorite
        item.updated_at = __import__("datetime").datetime.now().isoformat()
        item._data_encrypted = ""  # 不修改加密内容
        item._content_encrypted = ""
        self.database.update_item(item)
        self._refresh_content()

    def _on_copy_password(self, item: ItemModel):
        """复制密码到剪贴板。"""
        if item.password:
            self._copy_to_clipboard(item.password)
            self.status_label.setText(f"已复制 \"{item.title}\" 的密码")

    def _on_copy_account(self, item: ItemModel):
        """复制账号到剪贴板。"""
        if item.account:
            self._copy_to_clipboard(item.account)
            self.status_label.setText(f"已复制 \"{item.title}\" 的账号")

    def _on_open_document(self, item: ItemModel):
        """用系统程序打开文档。"""
        if item.stored_path:
            open_document_file(item.stored_path)

    # ---------- 工具方法 ----------

    def _copy_to_clipboard(self, text: str):
        """复制文本到系统剪贴板。"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _update_status_bar(self):
        """更新状态栏统计信息。"""
        items = self.database.get_items(category=self._current_category)
        count = len(items)
        self.status_label.setText(f"共 {count} 条")

    def _center_dialog(self, dialog):
        """将对话框居中于主窗口。"""
        parent_geo = self.geometry()
        size = dialog.size()
        x = parent_geo.x() + (parent_geo.width() - size.width()) // 2
        y = parent_geo.y() + (parent_geo.height() - size.height()) // 2
        dialog.move(x, y)

    # ---------- 锁定时的清理 ----------

    def lock(self):
        """
        锁定应用: 清除内存中的 Fernet 密钥和解密数据，显示空白状态。
        """
        self._fernet = None
        self.list_view.clear()
        self.list_view._item_models.clear()
        self.status_label.setText("已锁定")

    def closeEvent(self, event):
        """窗口关闭时清理数据库连接。"""
        self.database.set_setting("locked", "1")
        self._fernet = None
        self.database.close()
        event.accept()