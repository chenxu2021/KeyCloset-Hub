"""
KeyCloset Hub - 工具函数
包含数据目录初始化、时间格式化、文件操作等辅助功能。
"""

import os
import shutil
import uuid
from datetime import datetime


def ensure_data_dir() -> str:
    """
    确保数据根目录 ~/.keycloset/ 及其子目录存在。

    目录结构:
      ~/.keycloset/
      ├── keycloset.db       (数据库文件)
      ├── documents/         (文档本地副本)
      └── exports/           (笔记导出 .md)

    Returns:
        str: 数据根目录的绝对路径
    """
    base_dir = os.path.join(os.path.expanduser("~"), ".keycloset")
    os.makedirs(os.path.join(base_dir, "documents"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "exports"), exist_ok=True)
    return base_dir


def get_db_path() -> str:
    """
    获取数据库文件的完整路径。

    Returns:
        str: SQLite 数据库文件路径 (~/.keycloset/keycloset.db)
    """
    return os.path.join(ensure_data_dir(), "keycloset.db")


def get_documents_dir() -> str:
    """
    获取文档本地存储目录。

    Returns:
        str: 文档存储目录路径 (~/.keycloset/documents/)
    """
    return os.path.join(ensure_data_dir(), "documents")


def get_exports_dir() -> str:
    """
    获取笔记导出目录。

    Returns:
        str: 导出目录路径 (~/.keycloset/exports/)
    """
    return os.path.join(ensure_data_dir(), "exports")


def import_document(source_path: str) -> tuple:
    """
    将外部文件导入到本地文档存储目录。

    复制文件并以 UUID 重命名防止冲突，保留原始扩展名。

    Args:
        source_path: 源文件路径

    Returns:
        tuple: (stored_path: str, file_size: int, file_type: str)
               stored_path — 本地副本的绝对路径
               file_size — 文件大小 (字节)
               file_type — 文件扩展名 (不含点号)
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"源文件不存在: {source_path}")

    # 提取扩展名
    _, ext = os.path.splitext(source_path)
    file_type = ext.lstrip(".").lower() if ext else "unknown"

    # 生成唯一文件名
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(get_documents_dir(), unique_name)

    # 复制文件
    shutil.copy2(source_path, dest_path)

    # 获取文件大小
    file_size = os.path.getsize(dest_path)

    return dest_path, file_size, file_type


def export_note(title: str, content: str) -> str:
    """
    将笔记内容导出为 .md 文件。

    文件名格式: {清理后的标题}_{时间戳}.md

    Args:
        title: 笔记标题
        content: Markdown 内容

    Returns:
        str: 导出文件的完整路径
    """
    # 清理标题，移除不适合作为文件名的字符
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()
    if not safe_title:
        safe_title = "untitled"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_title}_{timestamp}.md"
    filepath = os.path.join(get_exports_dir(), filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def format_relative_time(iso_time: str) -> str:
    """
    将 ISO 格式时间转为相对时间字符串 (用于列表摘要)。

    规则:
      - 1 分钟内 → "刚刚"
      - 1 小时内 → "X 分钟前"
      - 24 小时内 → "X 小时前"
      - 7 天内 → "X 天前"
      - 超过 7 天 → "MM-DD HH:MM"
      - 超过 1 年 → "YYYY-MM-DD"

    Args:
        iso_time: ISO 格式时间字符串

    Returns:
        str: 友好的相对时间描述
    """
    if not iso_time:
        return ""

    try:
        dt = datetime.fromisoformat(iso_time)
        now = datetime.now()
        diff = now - dt

        seconds = diff.total_seconds()

        if seconds < 60:
            return "刚刚"
        elif seconds < 3600:
            return f"{int(seconds // 60)} 分钟前"
        elif seconds < 86400:
            return f"{int(seconds // 3600)} 小时前"
        elif seconds < 604800:
            return f"{int(seconds // 86400)} 天前"
        elif dt.year == now.year:
            return dt.strftime("%m-%d %H:%M")
        else:
            return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_time[:10] if len(iso_time) >= 10 else iso_time