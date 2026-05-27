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
    "bg_window": "#FFFFFF",
    "bg_sidebar": "#F5F5F5",
    "bg_titlebar": "#FAFAFA",
    "bg_input": "#FFFFFF",
    "bg_hover": "#EEEEEE",
    "bg_selected": "#E8E8E8",
    "bg_button": "#F0F0F0",
    "text_primary": "#1A1A1A",
    "text_secondary": "#999999",
    "text_placeholder": "#BBBBBB",
    "text_inverse": "#FFFFFF",
    "border_light": "#E5E5E5",
    "border_input": "#DDDDDD",
    "border_focus": "#333333",
    "accent": "#333333",
    "accent_hover": "#555555",
    "accent_text": "#1A1A1A",
    "danger": "#666666",
    "danger_hover": "#444444",
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
    "toolbar_height": 40,
    "list_item_height": 56,
    "border_radius_sm": 6,
    "border_radius_md": 10,
    "border_radius_lg": 14,
    "border_radius_window": 12,
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

# ---------- 阴影常量 ----------

SHADOW = {
    "blur_radius": 24,
    "offset_x": 0,
    "offset_y": 4,
    "color_alpha": 60,
}

# ---------- 全局 QSS 样式表 ----------

GLOBAL_STYLESHEET = """
QWidget {
    background-color: #FFFFFF;
    color: #1A1A1A;
    font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 12px;
    border: none;
    outline: none;
}
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
QScrollBar::handle:vertical:hover { background: #B0B0B0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal { background: #F5F5F5; height: 6px; margin: 0; border-radius: 3px; }
QScrollBar::handle:horizontal { background: #D0D0D0; min-width: 30px; border-radius: 3px; }
QScrollBar::handle:horizontal:hover { background: #B0B0B0; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF; color: #1A1A1A;
    border: 1px solid #DDDDDD; border-radius: 6px;
    padding: 6px 10px; font-size: 12px;
    selection-background-color: #E8E8E8; selection-color: #1A1A1A;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus { border: 1px solid #333333; }
QLineEdit::placeholder { color: #BBBBBB; }
QPushButton {
    background-color: #F0F0F0; color: #1A1A1A;
    border: 1px solid #E5E5E5; border-radius: 6px;
    padding: 6px 16px; font-size: 12px; min-height: 24px;
}
QPushButton:hover { background-color: #EEEEEE; border: 1px solid #CCCCCC; }
QPushButton:pressed { background-color: #E0E0E0; }
QPushButton:flat { background-color: transparent; border: none; }
QPushButton:flat:hover { background-color: #EEEEEE; }
QLabel { background-color: transparent; color: #1A1A1A; border: none; }
QListWidget, QTreeWidget, QTableWidget {
    background-color: #FFFFFF; color: #1A1A1A;
    border: none; outline: none; font-size: 12px;
}
QListWidget::item, QTreeWidget::item { padding: 8px 12px; border: none; }
QListWidget::item:hover, QTreeWidget::item:hover { background-color: #EEEEEE; }
QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #E8E8E8; color: #1A1A1A;
}
QComboBox {
    background-color: #FFFFFF; color: #1A1A1A;
    border: 1px solid #DDDDDD; border-radius: 6px;
    padding: 6px 10px; font-size: 12px;
}
QComboBox:hover { border: 1px solid #CCCCCC; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #FFFFFF; border: 1px solid #E5E5E5;
    selection-background-color: #E8E8E8;
}
QToolTip { background-color: #333333; color: #FFFFFF; border: none; border-radius: 6px; padding: 4px 8px; font-size: 11px; }
QStatusBar { background-color: #FAFAFA; color: #999999; border-top: 1px solid #E5E5E5; font-size: 11px; padding: 2px 8px; }
QFrame[frameShape="4"], QFrame[frameShape="5"] { color: #E5E5E5; }
QTabWidget::pane { border: none; background-color: #FFFFFF; }
QTabBar::tab {
    background-color: #F5F5F5; color: #999999;
    padding: 8px 16px; border: none;
    border-bottom: 2px solid transparent; font-size: 12px;
}
QTabBar::tab:hover { color: #1A1A1A; }
QTabBar::tab:selected { background-color: #FFFFFF; color: #1A1A1A; border-bottom: 2px solid #333333; }
"""

SIDEBAR_STYLESHEET = """
QListWidget { background-color: #F5F5F5; border: none; outline: none; padding: 8px 0; }
QListWidget::item {
    background-color: transparent; color: #1A1A1A;
    padding: 8px 16px; border: none; border-radius: 6px;
    margin: 1px 8px; font-size: 12px;
}
QListWidget::item:hover { background-color: #E8E8E8; }
QListWidget::item:selected { background-color: #E0E0E0; color: #1A1A1A; font-weight: normal; }
"""

LIST_ITEM_STYLESHEET = """
QListWidget { background-color: #FFFFFF; border: none; outline: none; padding: 0; }
QListWidget::item { background-color: transparent; border: none; border-bottom: 1px solid #F0F0F0; padding: 0; margin: 0; }
QListWidget::item:hover { background-color: #FAFAFA; }
QListWidget::item:selected { background-color: #F5F5F5; color: #1A1A1A; }
"""

SEARCH_BAR_STYLESHEET = """
QLineEdit {
    background-color: #F0F0F0; color: #1A1A1A;
    border: none; border-radius: 8px;
    padding: 6px 12px 6px 30px; font-size: 12px;
    min-height: 20px; max-height: 28px;
}
QLineEdit:focus { background-color: #EBEBEB; border: none; }
QLineEdit::placeholder { color: #AAAAAA; }
"""

# ---------- 现代化图标生成 ----------

import math
from PyQt5.QtCore import Qt, QSize, QPointF
from PyQt5.QtGui import QIcon, QPainter, QPen, QBrush, QColor, QPixmap, QPainterPath

_MODERN_ICONS = None


def generate_modern_icons():
    icons = {}
    size = QSize(18, 18)
    color = QColor("#555555")

    def _make_pix():
        p = QPixmap(size)
        p.fill(Qt.transparent)
        return p

    # password icon
    pix = _make_pix()
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    body = QPainterPath()
    body.addRoundedRect(4, 7, 10, 8, 2, 2)
    p.drawPath(body)
    p.drawArc(6, 2, 6, 6, 0, 180 * 16)
    p.setBrush(QBrush(color))
    p.drawEllipse(QPointF(9, 12), 1.5, 1.5)
    p.end()
    icons["password"] = QIcon(pix)

    # note icon
    pix = _make_pix()
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    path = QPainterPath()
    path.moveTo(5, 2); path.lineTo(10, 2); path.lineTo(14, 6); path.lineTo(14, 15); path.lineTo(5, 15)
    path.closeSubpath()
    p.drawPath(path)
    p.drawLine(10, 2, 10, 6); p.drawLine(10, 6, 14, 6)
    p.setPen(QPen(color, 1, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(7, 9, 12, 9); p.drawLine(7, 11.5, 12, 11.5)
    p.end()
    icons["note"] = QIcon(pix)

    # document icon
    pix = _make_pix()
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    path = QPainterPath()
    path.moveTo(3, 4); path.lineTo(7, 4); path.lineTo(8.5, 3); path.lineTo(11, 3); path.lineTo(11, 4)
    path.lineTo(15, 4); path.lineTo(15, 14); path.lineTo(3, 14)
    path.closeSubpath()
    p.drawPath(path)
    p.end()
    icons["document"] = QIcon(pix)

    # favorite / star icons
    def _draw_star(painter, filled):
        painter.setRenderHint(QPainter.Antialiasing)
        if filled:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color))
        else:
            painter.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(Qt.NoBrush)
        pts = []
        for i in range(10):
            angle = -math.pi / 2 + (i * math.pi / 5)
            r = 6 if i % 2 == 0 else 2.5
            pts.append(QPointF(9 + r * math.cos(angle), 9 + r * math.sin(angle)))
        star_path = QPainterPath()
        star_path.moveTo(pts[0])
        for pt in pts[1:]:
            star_path.lineTo(pt)
        star_path.closeSubpath()
        # smooth with rounded polygon approximation
        poly = star_path.toFillPolygon()
        sp = QPainterPath()
        for i2 in range(len(poly)):
            p0 = poly[(i2 - 1) % len(poly)]
            p1 = poly[i2]
            p2 = poly[(i2 + 1) % len(poly)]
            mid1 = QPointF((p0.x() + p1.x()) / 2, (p0.y() + p1.y()) / 2)
            mid2 = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
            if i2 == 0:
                sp.moveTo((mid1.x() + p1.x()) / 2, (mid1.y() + p1.y()) / 2)
            sp.quadTo(mid1, p1)
            sp.quadTo(p1, mid2)
        sp.closeSubpath()
        painter.drawPath(sp)

    pix = _make_pix()
    p = QPainter(pix)
    _draw_star(p, False)
    p.end()
    icons["star"] = QIcon(pix)
    icons["favorite"] = QIcon(pix)

    pix = _make_pix()
    p = QPainter(pix)
    _draw_star(p, True)
    p.end()
    icons["star_filled"] = QIcon(pix)

    # lock icon
    pix = _make_pix()
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    body2 = QPainterPath()
    body2.addRoundedRect(4, 7, 10, 8, 2, 2)
    p.drawPath(body2)
    p.drawArc(6, 2, 6, 6, 0, 180 * 16)
    p.setBrush(QBrush(color))
    p.drawEllipse(QPointF(9, 12), 1.2, 1.2)
    p.end()
    icons["lock"] = QIcon(pix)

    # add icon
    pix = _make_pix()
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(color, 1.8, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(9, 4, 9, 14)
    p.drawLine(4, 9, 14, 9)
    p.end()
    icons["add"] = QIcon(pix)

    return icons


def get_icon(key):
    global _MODERN_ICONS
    if _MODERN_ICONS is None:
        _MODERN_ICONS = generate_modern_icons()
    return _MODERN_ICONS.get(key, QIcon())