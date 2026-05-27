"""
KeyCloset Hub - 启动入口
极简启动脚本，初始化应用并进入事件循环。

运行方式:
    python main.py

环境要求:
    Python 3.8+, PyQt5, cryptography, markdown, Pygments
    详见 requirements.txt
"""

import sys
import os

# 将 KeyCloset_Hub 目录加入 sys.path，确保可以导入 keycloset 包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keycloset.app import KeyClosetApp


def main():
    """应用主入口函数。"""
    app = KeyClosetApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()