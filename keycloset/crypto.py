"""
KeyCloset Hub - 加密模块
实现 PBKDF2 + Fernet 加解密，保障所有敏感数据安全。

安全设计:
  1. 主密码通过 PBKDF2HMAC(SHA256, 480,000 轮) 派生 32 字节密钥
  2. 派生密钥经 base64 编码后作为 Fernet 加密密钥
  3. 随机 salt 持久化到数据库(明文)，每次解锁时读取
  4. 密码原文从不落盘 — 仅存储 salt 和加密后的验证短语
  5. 应用锁定时清除内存中的密钥和所有解密数据
"""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# PBKDF2 迭代次数 — 480,000 轮，OWASP 推荐的 SHA256 最低次数
PBKDF2_ITERATIONS = 480_000

# 用于验证主密码正确性的固定短语 (存储时会被 Fernet 加密)
VERIFICATION_PHRASE = b"KEYCLOSET_HUB_VERIFIED"


def generate_salt() -> bytes:
    """
    生成 16 字节密码学安全随机盐。

    Returns:
        bytes: 16 字节随机盐
    """
    return os.urandom(16)


def derive_key(master_password: str, salt: bytes) -> bytes:
    """
    通过 PBKDF2HMAC 从主密码和盐派生 32 字节密钥。

    Args:
        master_password: 用户输入的主密码 (明文)
        salt: 16 字节随机盐

    Returns:
        bytes: base64 编码后的 Fernet 兼容密钥 (44 字节)
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend(),
    )
    raw_key = kdf.derive(master_password.encode("utf-8"))
    # Fernet 需要 URL-safe base64 编码的 32 字节密钥
    return base64.urlsafe_b64encode(raw_key)


def create_verification_data(master_password: str) -> tuple:
    """
    首次设置主密码时调用:
      生成 salt → 派生密钥 → 加密验证短语 → 返回 (salt_hex, encrypted_phrase)

    Args:
        master_password: 用户设置的主密码

    Returns:
        tuple: (salt_hex: str, encrypted_phrase: str)
               salt_hex 存数据库明文，encrypted_phrase 用于后续验证
    """
    salt = generate_salt()
    key = derive_key(master_password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(VERIFICATION_PHRASE)
    return salt.hex(), encrypted.decode("utf-8")


def verify_master_password(master_password: str, salt_hex: str, encrypted_phrase: str) -> bool:
    """
    解锁时验证主密码是否正确。

    Args:
        master_password: 用户输入的主密码
        salt_hex: 数据库中存储的 salt (hex 字符串)
        encrypted_phrase: 数据库中存储的加密验证短语

    Returns:
        bool: True 表示密码正确
    """
    try:
        salt = bytes.fromhex(salt_hex)
        key = derive_key(master_password, salt)
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_phrase.encode("utf-8"))
        return decrypted == VERIFICATION_PHRASE
    except Exception:
        # 解密失败意味着密码错误或数据损坏
        return False


def get_fernet(master_password: str, salt_hex: str) -> Fernet:
    """
    解锁成功后获取 Fernet 实例，用于后续加解密操作。

    Args:
        master_password: 已验证正确的主密码
        salt_hex: 数据库中存储的 salt (hex 字符串)

    Returns:
        Fernet: 已初始化的 Fernet 加密对象
    """
    salt = bytes.fromhex(salt_hex)
    key = derive_key(master_password, salt)
    return Fernet(key)


def encrypt_data(fernet: Fernet, plaintext: str) -> str:
    """
    使用 Fernet 加密字符串数据。

    Args:
        fernet: 已初始化的 Fernet 实例
        plaintext: 明文字符串

    Returns:
        str: base64 编码的密文 (UTF-8 字符串)
    """
    return fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_data(fernet: Fernet, ciphertext: str) -> str:
    """
    使用 Fernet 解密字符串数据。

    Args:
        fernet: 已初始化的 Fernet 实例
        ciphertext: base64 编码的密文 (UTF-8 字符串)

    Returns:
        str: 解密后的明文字符串。如果解密失败返回空字符串。
    """
    try:
        return fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""