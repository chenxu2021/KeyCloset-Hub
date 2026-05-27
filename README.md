# 🔐 KeyCloset Hub

> 统一密码管理 · Markdown 笔记 · 文档存储 — 极简本地安全工具

[![Python](https://img.shields.io/badge/Python-3.8+-333333?logo=python)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-555555)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-888888)](LICENSE)

**KeyCloset Hub** 是一款极简风格的本地桌面应用，整合了密码管理、Markdown 笔记和文档存储三大功能。所有敏感数据通过 **PBKDF2 + Fernet** 加密后存入本地 SQLite 数据库，无需网络连接，数据完全由你掌控。

---

## ✨ 功能概览

| 模块 | 功能 |
|------|------|
| 🔑 **密码管理** | 存储网址/账号/密码/备注，一键复制账号或密码，随机密码生成 |
| 📝 **Markdown 笔记** | 完整 Markdown 编辑 + HTML 实时预览（代码高亮），导出 `.md` |
| 📁 **文档存储** | 拖拽导入文件，本地副本 UUID 命名，系统默认程序打开 |
| ⭐ **收藏 & 标签** | 任意条目加星标收藏，标签自由归类 |
| 🔍 **全局搜索** | 搜索标题 + 标签，`Ctrl+F` 聚焦 |
| 🔒 **安全锁定** | 5 分钟无操作自动锁定，`Ctrl+L` 手动锁定 |

---

## 🎨 设计风格

借鉴 **Things 3** 和 **Pass for iOS** 的极简美学：

- 严格的黑白灰配色，无彩色干扰
- 无边框自定义窗口，大量留白
- 操作按钮仅在悬停时浮现（`Enter/Leave` 事件）
- 双行列表：标题 + 摘要信息

<div align="center">
  <img src="screenshots/main_window.png" alt="主界面" width="700">
</div>

---

## 🔐 安全机制

```
用户主密码
    │
    ▼
PBKDF2HMAC(SHA256, 480,000 轮) + 随机 Salt
    │
    ▼
Fernet 对称加密密钥 (仅存内存)
    │
    ├── 密码条目 → JSON → Fernet 加密 → SQLite data_encrypted
    ├── 笔记内容 → Fernet 加密 → SQLite content_encrypted
    └── 文档元数据 → 明文存储 → SQLite
```

- **主密码从不落盘** — 仅存储 salt 和加密验证短语
- **锁定即销毁密钥** — 5 分钟空闲触发，内存中 Fernet 实例和所有解密数据立即清除
- **数据库权限** — 文件设为 `0o600`（仅当前用户可读写）

---

## 📁 项目结构

```
KeyCloset_Hub/
├── main.py                     # 启动入口
├── requirements.txt            # Python 依赖清单
├── build.bat                   # PyInstaller 一键打包脚本
├── README.md                   # 项目说明文档
├── .gitignore
└── keycloset/                  # 核心包
    ├── __init__.py
    ├── app.py                  # QApplication 生命周期 + 空闲锁定
    ├── crypto.py               # PBKDF2 + Fernet 加解密
    ├── database.py             # SQLite 初始化 & CRUD
    ├── models.py               # 统一数据模型 (ItemModel)
    ├── utils.py                # 工具函数 (数据目录/文件操作/时间格式化)
    └── ui/                     # UI 模块
        ├── __init__.py
        ├── theme.py            # 黑白灰配色 + QSS 样式表
        ├── login_dialog.py     # 解锁/设置主密码对话框
        ├── sidebar.py          # 左侧分类 & 标签导航
        ├── list_view.py        # 右侧双行列表 (悬停操作按钮)
        ├── search_bar.py       # 全局搜索栏
        ├── password_editor.py  # 密码条目编辑器
        ├── note_editor.py      # Markdown 编辑 + HTML 预览
        ├── document_view.py    # 文档导入 & 系统打开
        └── main_window.py      # 无边框主窗口整合
```

---

## 📦 数据持久化

运行时自动创建 `~/.keycloset/` 目录：

```
~/.keycloset/
├── keycloset.db          # SQLite 数据库 (加密存储)
├── documents/            # 导入文档的本地副本
│   ├── a1b2c3d4.pdf
│   └── e5f6g7h8.png
└── exports/              # 笔记导出 .md 文件
    └── meeting_notes_20260526.md
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows / macOS / Linux

### 安装 & 运行

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/KeyCloset-Hub.git
cd KeyCloset-Hub

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python main.py
```

### 打包为独立 .exe

```bash
pip install pyinstaller
build.bat
# 输出: dist/KeyClosetHub.exe
```

---

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + F` | 聚焦全局搜索 |
| `Ctrl + N` | 新增当前分类条目 |
| `Ctrl + E` | 编辑选中条目 |
| `Ctrl + C` | 复制密码 / 笔记内容 |
| `Ctrl + L` | 立即锁定应用 |
| `Esc` | 清空搜索 / 取消选择 |

---

## 🛠️ 技术栈

| 层面 | 技术 |
|------|------|
| GUI 框架 | PyQt5 (FramelessWindowHint 无边框) |
| 加密 | cryptography (Fernet + PBKDF2HMAC) |
| 数据库 | SQLite3 (sqlite3 内置模块) |
| Markdown | markdown (extra + codehilite 扩展) |
| 代码高亮 | Pygments |
| 打包 | PyInstaller (--onefile --windowed) |

---

## 📄 License

MIT © 2026