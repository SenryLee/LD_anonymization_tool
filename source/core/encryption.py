"""
加密解密功能模块
提供文本加密和解密功能
"""

import base64
import os
from dataclasses import dataclass

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    raise ImportError(
        "缺少依赖库 cryptography，请先安装：pip install cryptography"
    )


class Config:
    """加密配置常量"""
    SALT_LENGTH = 16
    NONCE_LENGTH = 12
    PBKDF2_ITERATIONS = 120000
    KEY_LENGTH = 32


@dataclass
class EncryptionResult:
    """加密结果数据类"""
    salt: str
    nonce: str
    data: str
    created_at: str
    version: str
    original_length: int
    masked_keywords: list


def derive_key(password: str, salt: bytes) -> bytes:
    """从密码派生加密密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=Config.KEY_LENGTH,
        salt=salt,
        iterations=Config.PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_text(text: str, password: str, keywords: list) -> EncryptionResult:
    """加密原文并保存元数据"""
    salt = os.urandom(Config.SALT_LENGTH)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(Config.NONCE_LENGTH)
    data = aesgcm.encrypt(nonce, text.encode("utf-8"), None)

    return EncryptionResult(
        salt=base64.b64encode(salt).decode("utf-8"),
        nonce=base64.b64encode(nonce).decode("utf-8"),
        data=base64.b64encode(data).decode("utf-8"),
        created_at="",  # 由调用方设置
        version="2.0",
        original_length=len(text),
        masked_keywords=keywords
    )


def decrypt_text(payload: dict, password: str) -> str:
    """解密还原原文"""
    try:
        salt = base64.b64decode(payload["salt"])
        nonce = base64.b64decode(payload["nonce"])
        data = base64.b64decode(payload["data"])
        key = derive_key(password, salt)
        aesgcm = AESGCM(key)
        plain = aesgcm.decrypt(nonce, data, None)
        return plain.decode("utf-8")
    except (KeyError, ValueError) as e:
        raise ValueError("加密文件格式错误或已损坏") from e
