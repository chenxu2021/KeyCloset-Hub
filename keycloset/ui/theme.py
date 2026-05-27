"""
KeyCloset Hub - 主题模块
定义全局黑白灰配色方案和 QSS 样式表。

设计风格: 借鉴 Things 3 和 Pass for iOS
  - 严格的黑白灰色调，无彩色
  - 大量留白，低视觉密度
  - 细线分隔，无重边框
  - 圆角按钮，柔和过渡
  - 自定义无边框窗口
"""

# ---------- 配色常量 ----------

COLORS = {
    # 背景色
    "bg_window": "#FFFFFF",  # 主窗口背景 — 纯白
    "bg_sidebar": "#F5F5F5",  # 侧边栏背景 — 极浅灰
    "bg_titlebar": "#FAFAFA",  # 标题栏背景 — 近白
    "bg_input": "#FFFFFF",  # 输入框背景 — 白
    "bg_hover": "#EEEEEE",  # 鼠标悬停 — 浅灰
    "bg_selected": "#E8E8E8",  # 选中状态 — 中浅灰
    "bg_button": "#F0F0F0",  # 按钮默认背景

    # 文字色
    "text_primary": "#1A1A1A",  # 主文字 — 近黑
    "text_secondary": "#999999",  # 次要文字 — 中灰
    "text_placeholder": "#BBBBBB",  # 占位符 — 浅灰
    "text_inverse": "#FFFFFF",  # 反白文字 — 纯白

    # 边框 & 分割线
    "border_light": "#E5E5E5",  # 浅分割线
    "border_input": "#DDDDDD",  # 输入框边框
    "border_focus": "#333333",  # 聚焦边框 — 深灰

    # 强调色 (深灰代替传统的蓝色)
    "accent": "#333333",  # 主要强调
    "accent_hover": "#555555",  # 悬停加深
    "accent_text": "#1A1A1A",  # 强调文字

    # 状态色 (保持灰色调)
    "danger": "#666666",  # 删除/危险操作
    "danger_hover": "#444444",  # 危险操作悬停
}

# ---------- 尺寸常量 ----------

DIMENSIONS = {
    "window_width": 960,
    "window_height": 640,
    "window_min_width": 720,
    "window_min_height": 480,
    "sidebar_width": 220,
    "titlebar_height": 44,
    "statusbar_height": 32,
    "list_item_height": 56,
    "border_radius_sm": 4,
    "border_radius_md": 6,
    "border_radius_lg": 8,
    "font_size_title": 13,
    "font_size_body": 12,
    "font_size_small": 11,
    "font_size_sidebar": 12,
    "spacing_xs": 4,
    "spacing_sm": 8,
    "spacing_md": 12,
    "spacing_lg": 16,
    "spacing_xl": 24,
}

# ---------- 全局 QSS 样式表 ----------

GLOBAL_STYLESHEET = """
/* ===== 全局基样式 ===== */
QWidget {
    background-color: #FFFFFF;
    color: #1A1A1A;
    font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 12px;
    border: none;
    outline: none;
}

/* ===== 滚动条 ===== */
QScrollBar:vertical {
    background: #F5F5F5;
    width: 6px;
    margin: 0;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #D0D0D0;
    min-height: 30px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #B0B0B0;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background: #F5F5F5;
    height: 6px;
    margin: 0;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #D0D0D0;
    min-width: 30px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background: #B0B0B0;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ===== 输入框 ===== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #DDDDDD;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
    selection-background-color: #E8E8E8;
    selection-color: #1A1A1A;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #333333;
}
QLineEdit::placeholder {
    color: #BBBBBB;
}

/* ===== 按钮 ===== */
QPushButton {
    background-color: #F0F0F0;
    color: #1A1A1A;
    border: 1px solid #E5E5E5;
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 12px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #EEEEEE;
    border: 1px solid #CCCCCC;
}
QPushButton:pressed {
    background-color: #E0E0E0;
}
QPushButton:flat {
    background-color: transparent;
    border: none;
}
QPushButton:flat:hover {
    background-color: #EEEEEE;
}

/* ===== 标签 ===== */
QLabel {
    background-color: transparent;
    color: #1A1A1A;
    border: none;
}

/* ===== 列表控件 ===== */
QListWidget, QTreeWidget, QTableWidget {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: none;
    outline: none;
    font-size: 12px;
}
QListWidget::item, QTreeWidget::item {
    padding: 8px 12px;
    border: none;
}
QListWidget::item:hover, QTreeWidget::item:hover {
    background-color: #EEEEEE;
}
QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #E8E8E8;
    color: #1A1A1A;
}

/* ===== 下拉框 ===== */
QComboBox {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #DDDDDD;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}
QComboBox:hover {
    border: 1px solid #CCCCCC;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    selection-background-color: #E8E8E8;
}

/* ===== 提示框 ===== */
QToolTip {
    background-color: #333333;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
}

/* ===== 状态栏 ===== */
QStatusBar {
    background-color: #FAFAFA;
    color: #999999;
    border-top: 1px solid #E5E5E5;
    font-size: 11px;
    padding: 2px 8px;
}

/* ===== 分割线 ===== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #E5E5E5;
}

/* ===== Tab 控件 ===== */
QTabWidget::pane {
    border: none;
    background-color: #FFFFFF;
}
QTabBar::tab {
    background-color: #F5F5F5;
    color: #999999;
    padding: 8px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 12px;
}
QTabBar::tab:hover {
    color: #1A1A1A;
}
QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border-bottom: 2px solid #333333;
}
"""

# ---------- 侧边栏专用样式 ----------

SIDEBAR_STYLESHEET = """
QListWidget {
    background-color: #F5F5F5;
    border: none;
    outline: none;
    padding: 8px 0;
}
QListWidget::item {
    background-color: transparent;
    color: #1A1A1A;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    margin: 1px 8px;
    font-size: 12px;
}
QListWidget::item:hover {
    background-color: #E8E8E8;
}
QListWidget::item:selected {
    background-color: #E0E0E0;
    color: #1A1A1A;
    font-weight: normal;
}
"""

# ---------- 列表条目专用样式 ----------

LIST_ITEM_STYLESHEET = """
QListWidget {
    background-color: #FFFFFF;
    border: none;
    outline: none;
    padding: 0;
}
QListWidget::item {
    background-color: transparent;
    border: none;
    border-bottom: 1px solid #F0F0F0;
    padding: 0;
    margin: 0;
}
QListWidget::item:hover {
    background-color: #FAFAFA;
}
QListWidget::item:selected {
    background-color: #F5F5F5;
    color: #1A1A1A;
}
"""

# ---------- 搜索框专用样式 ----------

SEARCH_BAR_STYLESHEET = """
QLineEdit {
    background-color: #F0F0F0;
    color: #1A1A1A;
    border: none;
    border-radius: 6px;
    padding: 6px 12px 6px 30px;
    font-size: 12px;
    min-height: 20px;
    max-height: 28px;
}
QLineEdit:focus {
    background-color: #EBEBEB;
    border: none;
}
QLineEdit::placeholder {
    color: #AAAAAA;
}
"""