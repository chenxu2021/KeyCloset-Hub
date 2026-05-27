"""
KeyCloset Hub - 数据库模块
SQLite 数据库初始化、CRUD 操作、数据生命周期管理。

设计要点:
  1. 单例模式 — 整个应用生命周期内仅一个数据库连接
  2. 所有增删改操作后自动 commit，保证数据持久化
  3. 文档删除时级联删除本地文件
  4. 数据库文件权限设为 0o600 (仅当前用户可读写)
  5. WAL 模式关闭 (单用户本地应用不需要并发)
"""

import json
import os
import sqlite3
import stat
from typing import Optional

from .models import ItemModel


class Database:
    """
    数据库管理类 — 封装所有 SQLite 操作。
    """

    def __init__(self, db_path: str):
        """
        初始化数据库连接。

        Args:
            db_path: SQLite 数据库文件路径 (如 ~/.keycloset/keycloset.db)
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()

    def _connect(self):
        """建立数据库连接并初始化表结构。"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 让查询结果支持列名访问
        self.conn.execute("PRAGMA journal_mode=DELETE")  # 关闭 WAL 模式
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._init_tables()
        self._secure_file()

    def _secure_file(self):
        """设置数据库文件权限为仅当前用户可读写 (Unix/Windows 兼容)。"""
        try:
            if os.path.exists(self.db_path):
                os.chmod(self.db_path, stat.S_IREAD | stat.S_IWRITE)
        except Exception:
            pass  # Windows 下 chmod 行为不同，忽略异常

    def _init_tables(self):
        """
        创建数据库表结构:
          - settings: 存储加密元数据 (salt, 验证短语, 锁定状态)
          - items: 统一存储所有条目 (密码/笔记/文档)
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                category          TEXT NOT NULL,
                title             TEXT NOT NULL DEFAULT '',
                summary           TEXT NOT NULL DEFAULT '',
                tags              TEXT NOT NULL DEFAULT '[]',
                is_favorite       INTEGER NOT NULL DEFAULT 0,
                data_encrypted    TEXT DEFAULT '',
                content_encrypted TEXT DEFAULT '',
                file_path         TEXT DEFAULT '',
                stored_path       TEXT DEFAULT '',
                file_size         INTEGER DEFAULT 0,
                file_type         TEXT DEFAULT '',
                created_at        TEXT NOT NULL,
                updated_at        TEXT NOT NULL
            )
        """)

        # 为常用查询字段建立索引，加速搜索和分类筛选
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_category
            ON items(category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_favorite
            ON items(is_favorite)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_updated
            ON items(updated_at DESC)
        """)

        self.conn.commit()

    # ---------- settings 表操作 ----------

    def set_setting(self, key: str, value: str):
        """
        写入或更新配置项。

        Args:
            key: 配置键名
            value: 配置值
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        self.conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        """
        读取配置项。

        Args:
            key: 配置键名
            default: 默认值 (键不存在时返回)

        Returns:
            str: 配置值
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

    # ---------- items 表 CRUD ----------

    def add_item(self, item: ItemModel) -> int:
        """
        插入新条目。

        Args:
            item: 条目数据模型

        Returns:
            int: 新插入条目的自增 ID
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO items
                (category, title, summary, tags, is_favorite,
                 data_encrypted, content_encrypted,
                 file_path, stored_path, file_size, file_type,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.category,
                item.title,
                item.summary,
                json.dumps(item.tags, ensure_ascii=False),
                1 if item.is_favorite else 0,
                "",  # data_encrypted — 由调用方加密后通过 update_item 写入
                "",  # content_encrypted — 同上
                item.file_path,
                item.stored_path,
                item.file_size,
                item.file_type,
                item.created_at,
                item.updated_at,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_item(self, item: ItemModel):
        """
        更新现有条目。根据 ID 定位。

        Args:
            item: 包含 id 字段的条目模型
        """
        if item.id is None:
            raise ValueError("更新条目时 id 不能为 None")
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE items SET
                title = ?,
                summary = ?,
                tags = ?,
                is_favorite = ?,
                data_encrypted = ?,
                content_encrypted = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                item.title,
                item.summary,
                json.dumps(item.tags, ensure_ascii=False),
                1 if item.is_favorite else 0,
                getattr(item, "_data_encrypted", ""),
                getattr(item, "_content_encrypted", ""),
                item.updated_at,
                item.id,
            ),
        )
        self.conn.commit()

    def delete_item(self, item_id: int):
        """
        删除条目，如果是文档类型则同时删除本地文件副本。

        Args:
            item_id: 条目 ID
        """
        # 先查出条目信息，用于清理文件
        item = self.get_item_by_id(item_id)
        if item and item.category == "document" and item.stored_path:
            # 删除本地文档副本
            try:
                if os.path.exists(item.stored_path):
                    os.remove(item.stored_path)
            except Exception:
                pass  # 文件删除失败不阻塞数据库操作

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.conn.commit()

    def get_item_by_id(self, item_id: int) -> Optional[ItemModel]:
        """
        根据 ID 获取单条记录。

        Args:
            item_id: 条目 ID

        Returns:
            ItemModel | None: 找到则返回模型实例，否则返回 None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_item(row)

    def get_items(
        self,
        category: Optional[str] = None,
        search_query: str = "",
    ) -> list:
        """
        获取条目列表，支持按分类筛选和文本搜索。

        Args:
            category: 分类键名:
                      "password" / "note" / "document" — 按分类筛选
                      "favorite" — 筛选收藏条目
                      None — 返回全部条目 (用于全局搜索)
            search_query: 搜索关键词 (空字符串表示不过滤)

        Returns:
            list[ItemModel]: 匹配的条目列表，按更新时间倒序排列
        """
        cursor = self.conn.cursor()

        # 构建 SQL 查询
        conditions = []
        params = []

        if category == "favorite":
            conditions.append("is_favorite = 1")
        elif category and category in ("password", "note", "document"):
            conditions.append("category = ?")
            params.append(category)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM items WHERE {where_clause} ORDER BY updated_at DESC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        items = [self._row_to_item(row) for row in rows]

        # 如果提供了搜索关键词，在 Python 层面做二次过滤
        # (因为加密字段无法在 SQL 层面搜索)
        if search_query:
            items = [item for item in items if item.matches_search(search_query)]

        return items

    def get_all_tags(self) -> list:
        """
        获取所有不重复的标签列表，用于侧边栏标签展示。

        Returns:
            list[str]: 排序后的标签字符串列表
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT tags FROM items")
        rows = cursor.fetchall()

        all_tags = set()
        for row in rows:
            try:
                tag_list = json.loads(row["tags"])
                all_tags.update(tag_list)
            except (json.JSONDecodeError, TypeError):
                pass

        return sorted(all_tags)

    def _row_to_item(self, row: sqlite3.Row) -> ItemModel:
        """
        将数据库行转换为 ItemModel 实例。

        Args:
            row: 数据库查询结果行

        Returns:
            ItemModel: 模型实例
        """
        try:
            tags = json.loads(row["tags"])
        except (json.JSONDecodeError, TypeError):
            tags = []

        return ItemModel(
            id=row["id"],
            category=row["category"],
            title=row["title"],
            summary=row["summary"],
            tags=tags,
            is_favorite=bool(row["is_favorite"]),
            file_path=row["file_path"],
            stored_path=row["stored_path"],
            file_size=row["file_size"],
            file_type=row["file_type"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            # 加密字段不会直接放在 ItemModel 中，由调用方解密后填入
        )

    def close(self):
        """关闭数据库连接。"""
        if self.conn:
            self.conn.close()
            self.conn = None