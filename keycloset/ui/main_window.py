"""
KeyCloset Hub - 主窗口 (v2.0 — 圆角窗口 + 阴影 + 工具栏 + 空状态 + toast)
"""

import json
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer, QRectF, QPropertyAnimation, QPoint, QEasingCurve
from PyQt5.QtGui import QFont, QKeySequence, QPainterPath, QRegion, QColor
from PyQt5.QtWidgets import (
    QApplication, QGraphicsDropShadowEffect,
    QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QPushButton, QShortcut, QStatusBar, QVBoxLayout, QWidget, QSizePolicy,
)

from ..crypto import decrypt_data, encrypt_data, get_fernet
from ..database import Database
from ..models import ItemModel, CATEGORIES
from ..utils import format_relative_time, export_note
from .document_view import DocumentImporter, open_document_file
from .list_view import ItemListWidget
from .note_editor import NoteEditor
from .password_editor import PasswordEditor
from .search_bar import SearchBar
from .sidebar import Sidebar
from .theme import COLORS, DIMENSIONS, SHADOW, GLOBAL_STYLESHEET, get_icon


class MainWindow(QMainWindow):
    """KeyCloset Hub 主窗口 — 圆角 + 阴影 + 工具栏。"""

    def __init__(self, database: Database, master_password: str, lock_callback):
        super().__init__()
        self.database = database
        self.master_password = master_password
        self._lock_callback = lock_callback
        salt_hex = self.database.get_setting("salt")
        self._fernet = get_fernet(master_password, salt_hex)
        self._current_category = "password"
        self._search_query = ""
        self._setup_window()
        self._setup_shortcuts()
        self._apply_stylesheet()
        self._refresh_content()

    # ---------- 窗口搭建 ----------

    def _setup_window(self):
        self.setWindowTitle("KeyCloset Hub")
        self.setMinimumSize(DIMENSIONS["window_min_width"], DIMENSIONS["window_min_height"])
        self.resize(DIMENSIONS["window_width"], DIMENSIONS["window_height"])
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        # 外层容器 — 负责圆角和阴影
        self._container = QWidget(objectName="windowContainer")
        self._container.setStyleSheet(f"""
            #windowContainer {{
                background-color: {COLORS['bg_window']};
                border: 1px solid {COLORS['border_light']};
                border-radius: {DIMENSIONS['border_radius_window']}px;
            }}
        """)
        self.setCentralWidget(self._container)

        # 容器内布局
        outer = QVBoxLayout(self._container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # 标题栏
        self._titlebar = self._create_titlebar()
        outer.addWidget(self._titlebar)

        # 工具栏
        outer.addWidget(self._create_toolbar())

        # 主体：侧边栏 + 分割线 + 内容
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.category_changed.connect(self._on_category_changed)
        self.sidebar.tag_selected.connect(self._on_tag_selected)
        body_layout.addWidget(self.sidebar)

        divider = QWidget()
        divider.setFixedWidth(1)
        divider.setStyleSheet(f"background-color: {COLORS['border_light']};")
        body_layout.addWidget(divider)

        # 右侧内容（列表 + 空状态叠加层）
        content_stack = QWidget()
        content_stack_layout = QVBoxLayout(content_stack)
        content_stack_layout.setContentsMargins(0, 0, 0, 0)
        content_stack_layout.setSpacing(0)

        self.list_view = ItemListWidget()
        self.list_view.item_copy_password.connect(self._on_copy_password)
        self.list_view.item_copy_account.connect(self._on_copy_account)
        self.list_view.item_edit.connect(self._on_edit_item)
        self.list_view.item_delete.connect(self._on_delete_item)
        self.list_view.item_toggle_favorite.connect(self._on_toggle_favorite)
        self.list_view.item_open_file.connect(self._on_open_document)
        content_stack_layout.addWidget(self.list_view)

        # 空状态占位
        self._empty_label = QLabel()
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        self._empty_label.hide()
        content_stack_layout.addWidget(self._empty_label)

        body_layout.addWidget(content_stack)
        outer.addWidget(body)

        # 状态栏
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
        outer.addWidget(self.status_bar)
        self._update_status_bar()

    # ---------- 标题栏 ----------

    def _create_titlebar(self):
        tb = QWidget()
        tb.setFixedHeight(DIMENSIONS["titlebar_height"])
        tb.setStyleSheet(f"background-color: {COLORS['bg_titlebar']}; border-top-left-radius: {DIMENSIONS['border_radius_window']}px; border-top-right-radius: {DIMENSIONS['border_radius_window']}px;")
        tb.mousePressEvent = self._titlebar_mouse_press
        tb.mouseMoveEvent = self._titlebar_mouse_move
        tb.mouseDoubleClickEvent = self._titlebar_double_click
        layout = QHBoxLayout(tb)
        layout.setContentsMargins(16, 0, 4, 0)
        layout.setSpacing(0)
        app_label = QLabel("KeyCloset Hub")
        app_label.setFont(QFont("Segoe UI", 11))
        app_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        layout.addWidget(app_label)
        layout.addStretch()

        btn = ("QPushButton { background:transparent; border:none; border-radius:4px; "
               "padding:4px 10px; font-size:14px; color:#999; min-width:32px; } "
               "QPushButton:hover { background:#E8E8E8; color:#333; }")
        for text, slot in [("−", self.showMinimized), ("□", self._toggle_maximize), ("✕", self.close)]:
            b = QPushButton(text)
            b.setStyleSheet(btn)
            b.clicked.connect(slot)
            layout.addWidget(b)
        self._drag_pos = None
        return tb

    def _titlebar_mouse_press(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos()

    def _titlebar_mouse_move(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(self.pos() + e.globalPos() - self._drag_pos)
            self._drag_pos = e.globalPos()

    def _titlebar_double_click(self, e):
        self._toggle_maximize()

    def _toggle_maximize(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    # ---------- 工具栏 ----------

    def _create_toolbar(self):
        bar = QWidget()
        bar.setFixedHeight(DIMENSIONS["toolbar_height"])
        bar.setStyleSheet(f"background-color: {COLORS['bg_titlebar']}; border-bottom: 1px solid {COLORS['border_light']};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 4, 12, 4)
        layout.setSpacing(8)

        # 分类标题
        self.category_title = QLabel("密码")
        self.category_title.setFont(QFont("Segoe UI", 13))
        self.category_title.setStyleSheet(f"font-weight: 600; color: {COLORS['text_primary']};")
        layout.addWidget(self.category_title)

        layout.addStretch()

        # 新增按钮 (鼠标可点击)
        self._add_btn = QPushButton(" 新增")
        self._add_btn.setIcon(get_icon("add"))
        self._add_btn.setStyleSheet("""
            QPushButton { background:#F0F0F0; border:1px solid #DDD; border-radius:6px; padding:4px 12px; font-size:12px; }
            QPushButton:hover { background:#E5E5E5; }
        """)
        self._add_btn.clicked.connect(self._on_new_item)
        layout.addWidget(self._add_btn)

        # 锁定按钮
        self._lock_btn = QPushButton(" 锁定")
        self._lock_btn.setIcon(get_icon("lock"))
        self._lock_btn.setStyleSheet(self._add_btn.styleSheet())
        self._lock_btn.clicked.connect(self._handle_lock)
        layout.addWidget(self._lock_btn)

        # 搜索栏
        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self._on_search_changed)
        layout.addWidget(self.search_bar)

        return bar

    # ---------- 样式 ----------

    def _apply_stylesheet(self):
        self.setStyleSheet(GLOBAL_STYLESHEET)

    # ---------- 快捷键 ----------

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self, self.search_bar.focus_search)
        QShortcut(QKeySequence("Ctrl+N"), self, self._on_new_item)
        QShortcut(QKeySequence("Ctrl+E"), self, self._handle_edit_current)
        QShortcut(QKeySequence("Ctrl+C"), self, self._handle_copy)
        QShortcut(QKeySequence("Ctrl+L"), self, self._handle_lock)
        QShortcut(QKeySequence("Escape"), self, self._handle_escape)

    def _handle_edit_current(self):
        ci = self.list_view.currentItem()
        if ci:
            m = self.list_view._get_model_from_item(ci)
            if m:
                self._on_edit_item(m)

    def _handle_copy(self):
        ci = self.list_view.currentItem()
        if ci:
            m = self.list_view._get_model_from_item(ci)
            if m:
                if m.category == "password":
                    self._on_copy_password(m)
                elif m.category == "note":
                    self._copy_to_clipboard(m.content)
                else:
                    self._copy_to_clipboard(m.title)

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
        labels = {"password": "密码", "note": "笔记", "document": "文档", "favorite": "收藏"}
        self.category_title.setText(labels.get(self._current_category, "全部"))
        items = self.database.get_items(category=self._current_category, search_query=self._search_query)
        for item in items:
            self._decrypt_item(item)
        self.list_view.load_items(items)
        tags = self.database.get_all_tags()
        self.sidebar.update_tags(tags)

        # 空状态
        if not items:
            tips = {"password": "还没有密码条目\n点击 ＋ 新增", "note": "还没有笔记\n点击 ＋ 新建",
                    "document": "还没有文档\n拖拽文件或点击 ＋ 导入", "favorite": "还没有收藏\n点击 ☆ 收藏条目"}
            self._empty_label.setText(tips.get(self._current_category, ""))
            self._empty_label.show()
            self.list_view.hide()
        else:
            self._empty_label.hide()
            self.list_view.show()
        self._update_status_bar()

    def _decrypt_item(self, item):
        if not self._fernet or item.id is None:
            return
        row = self.database.conn.execute(
            "SELECT data_encrypted, content_encrypted FROM items WHERE id = ?", (item.id,)
        ).fetchone()
        if not row:
            return
        if item.category == "password" and row["data_encrypted"]:
            js = decrypt_data(self._fernet, row["data_encrypted"])
            if js:
                try:
                    d = json.loads(js)
                    item.url = d.get("url", "")
                    item.account = d.get("account", "")
                    item.password = d.get("password", "")
                    item.notes = d.get("notes", "")
                except json.JSONDecodeError:
                    pass
        elif item.category == "note" and row["content_encrypted"]:
            item.content = decrypt_data(self._fernet, row["content_encrypted"])

    # ---------- 保存 ----------

    def _save_password_item(self, item):
        enc = encrypt_data(self._fernet, json.dumps(item.to_dict(), ensure_ascii=False))
        if item.id is None:
            item.id = self.database.add_item(item)
        item._data_encrypted = enc
        item.updated_at = datetime.now().isoformat()
        self.database.update_item(item)

    def _save_note_item(self, item):
        enc = encrypt_data(self._fernet, item.content)
        if item.id is None:
            item.id = self.database.add_item(item)
        item._content_encrypted = enc
        item.updated_at = datetime.now().isoformat()
        self.database.update_item(item)

    def _save_document_item(self, item):
        if item.id is None:
            item.id = self.database.add_item(item)
        else:
            item._data_encrypted = ""
            item._content_encrypted = ""
            item.updated_at = datetime.now().isoformat()
            self.database.update_item(item)

    # ---------- 信号处理 ----------

    def _on_category_changed(self, cat):
        self._current_category = cat
        self.search_bar.clear()
        self._search_query = ""
        self._refresh_content()

    def _on_tag_selected(self, tag):
        self.search_bar.search_input.setText(tag)
        self._search_query = tag
        self._refresh_content()

    def _on_search_changed(self, q):
        self._search_query = q.strip()
        self._refresh_content()

    def _on_new_item(self):
        cat = self._current_category
        if cat == "favorite":
            cat = "password"
        if cat == "password":
            dlg = PasswordEditor(parent=self)
            dlg.item_saved.connect(self._on_password_saved)
        elif cat == "note":
            dlg = NoteEditor(parent=self)
            dlg.item_saved.connect(self._on_note_saved)
        elif cat == "document":
            dlg = DocumentImporter(parent=self)
            dlg.item_saved.connect(self._on_document_saved)
        else:
            return
        self._center_dialog(dlg)
        dlg.exec_()

    def _on_edit_item(self, item):
        if item.category == "password":
            dlg = PasswordEditor(item=item, parent=self)
            dlg.item_saved.connect(self._on_password_saved)
            self._center_dialog(dlg)
            dlg.exec_()
        elif item.category == "note":
            dlg = NoteEditor(item=item, parent=self)
            dlg.item_saved.connect(self._on_note_saved)
            self._center_dialog(dlg)
            dlg.exec_()

    def _on_password_saved(self, item):
        self._save_password_item(item)
        self._refresh_content()

    def _on_note_saved(self, item):
        self._save_note_item(item)
        self._refresh_content()

    def _on_document_saved(self, item):
        self._save_document_item(item)
        self._refresh_content()

    def _on_delete_item(self, item):
        r = QMessageBox.question(self, "确认删除", f"确定要删除 \"{item.title}\" 吗？",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r == QMessageBox.Yes:
            self.database.delete_item(item.id)
            self._refresh_content()

    def _on_toggle_favorite(self, item):
        item.is_favorite = not item.is_favorite
        item._data_encrypted = ""
        item._content_encrypted = ""
        item.updated_at = datetime.now().isoformat()
        self.database.update_item(item)
        self._refresh_content()

    def _on_copy_password(self, item):
        if item.password:
            self._copy_to_clipboard(item.password)
            self._show_toast(f"✓ 已复制 \"{item.title}\" 的密码")

    def _on_copy_account(self, item):
        if item.account:
            self._copy_to_clipboard(item.account)
            self._show_toast(f"✓ 已复制 \"{item.title}\" 的账号")

    def _on_open_document(self, item):
        if item.stored_path:
            open_document_file(item.stored_path)

    # ---------- Toast 提示 ----------

    def _show_toast(self, text):
        toast = QLabel(text, parent=self._container)
        toast.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['accent']};
                color: {COLORS['text_inverse']};
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 12px;
            }}
        """)
        toast.adjustSize()
        cw = self._container.width()
        ch = self._container.height()
        toast.move((cw - toast.width()) // 2, ch - toast.height() - 50)
        toast.show()

        # 渐隐动画
        anim = QPropertyAnimation(toast, b"windowOpacity")
        anim.setDuration(2000)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(toast.deleteLater)
        anim.start()

    # ---------- 工具 ----------

    def _copy_to_clipboard(self, text):
        QApplication.clipboard().setText(text)

    def _update_status_bar(self):
        items = self.database.get_items(category=self._current_category)
        self.status_label.setText(f"共 {len(items)} 条")

    def _center_dialog(self, dialog):
        # 使用屏幕几何确保首次显示也不会偏移
        geo = self.geometry()
        if geo.x() == 0 and geo.y() == 0:
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.primaryScreen().availableGeometry()
            geo.moveCenter(screen.center())
        sz = dialog.size()
        x = geo.x() + (geo.width() - sz.width()) // 2
        y = geo.y() + (geo.height() - sz.height()) // 2
        dialog.move(max(0, x), max(0, y))

    # ---------- 锁定 ----------

    def lock(self):
        self._fernet = None
        self.list_view.clear()
        self.list_view._item_models.clear()
        self.status_label.setText("已锁定")

    def closeEvent(self, event):
        self.database.set_setting("locked", "1")
        self._fernet = None
        self.database.close()
        event.accept()