"""
KeyCloset Hub - 数据模型
统一的数据结构定义，所有模块共用。

存储策略:
  - 密码条目的敏感字段 (url/account/password/notes) 以 JSON 序列化后 Fernet 加密存入 data_encrypted
  - 笔记正文以 Fernet 加密存入 content_encrypted
  - 文档元数据 (file_path/stored_path/file_size/file_type) 明文存储
  - 标题/摘要/标签/收藏标记 明文存储 (非敏感元数据)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ItemModel:
    """
    统一条目模型 — 适用于密码、笔记、文档三种类型。

    数据库映射:
      items 表的每一行对应一个 ItemModel 实例。
      加密字段 (data_encrypted, content_encrypted) 在插入前由调用方加密，
      查询后由调用方解密后填入 _decrypted_* 属性。
    """

    # 基本标识
    id: Optional[int] = None  # 数据库自增主键 (新建时为 None)
    category: str = "password"  # 分类: "password" | "note" | "document"

    # 明文元数据 — 用于列表显示和搜索
    title: str = ""  # 标题 (第一行)
    summary: str = ""  # 摘要 (第二行，如 "github.com · 2小时前")
    tags: list = field(default_factory=list)  # 标签列表，如 ["work", "personal"]
    is_favorite: bool = False  # 是否收藏

    # 密码模块专用 — JSON 序列化后加密存储 (data_encrypted 字段)
    url: str = ""
    account: str = ""
    password: str = ""
    notes: str = ""

    # 笔记模块专用 — 加密存储 (content_encrypted 字段)
    content: str = ""  # Markdown 原始文本

    # 文档模块专用 — 明文存储
    file_path: str = ""  # 原始文件路径 (导入时)
    stored_path: str = ""  # 本地副本路径 (data/documents/uuid.ext)
    file_size: int = 0  # 文件大小 (字节)
    file_type: str = ""  # 文件扩展名 (如 "pdf")

    # 时间戳
    created_at: str = ""  # ISO 格式创建时间
    updated_at: str = ""  # ISO 格式更新时间

    def __post_init__(self):
        """初始化时自动设置时间戳。"""
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict:
        """转为字典，用于 JSON 序列化 (密码模块)。"""
        return {
            "url": self.url,
            "account": self.account,
            "password": self.password,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict, category: str = "password") -> "ItemModel":
        """从字典创建实例。"""
        if category == "password":
            return cls(
                url=data.get("url", ""),
                account=data.get("account", ""),
                password=data.get("password", ""),
                notes=data.get("notes", ""),
            )
        return cls()

    def format_summary(self) -> str:
        """
        根据分类自动生成摘要字符串，用于列表第二行显示。
        """
        if self.category == "password":
            parts = []
            if self.url:
                # 提取域名部分作为摘要
                domain = self.url.replace("https://", "").replace("http://", "").split("/")[0]
                parts.append(domain)
            if self.account:
                parts.append(self.account)
            if not parts:
                parts.append("无额外信息")
            return " · ".join(parts)
        elif self.category == "note":
            # 取内容前 50 字符作为摘要
            preview = self.content[:50].replace("\n", " ")
            return preview if preview else "空笔记"
        elif self.category == "document":
            # 显示文件类型和大小
            size_str = self._format_size(self.file_size)
            return f"{self.file_type.upper()} · {size_str}"
        return ""

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """将字节数转为可读的文件大小字符串。"""
        for unit in ("B", "KB", "MB", "GB"):
            if size_bytes < 1024:
                return f"{size_bytes} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def matches_search(self, query: str) -> bool:
        """
        检查条目是否匹配搜索关键词。

        Args:
            query: 搜索关键词 (小写)

        Returns:
            bool: 标题、标签、或内容中出现关键词则返回 True
        """
        if not query:
            return True
        q = query.lower()
        # 匹配标题
        if q in self.title.lower():
            return True
        # 匹配标签
        if any(q in tag.lower() for tag in self.tags):
            return True
        # 匹配密码模块的账号和 URL
        if self.category == "password":
            if q in self.account.lower() or q in self.url.lower():
                return True
        # 匹配笔记摘要
        if self.category == "note":
            if q in self.summary.lower():
                return True
        return False


# 分类定义 — 侧边栏导航使用
CATEGORIES = [
    {"key": "password", "label": "密码", "icon": "password"},
    {"key": "note", "label": "笔记", "icon": "note"},
    {"key": "document", "label": "文档", "icon": "document"},
    {"key": "favorite", "label": "收藏", "icon": "favorite"},
]
