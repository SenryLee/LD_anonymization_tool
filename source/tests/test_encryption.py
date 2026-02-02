"""
加密解密功能单元测试
"""

import pytest
import json
from app import encrypt_text, decrypt_text, derive_key


class TestEncryption:
    """测试加密解密功能"""

    def test_encrypt_decrypt_roundtrip(self):
        """测试加密解密往返"""
        original_text = "这是一段需要加密的测试文本"
        password = "test_password_123"

        # 加密
        encrypted = encrypt_text(original_text, password, ["测试"])

        # 解密
        encrypted_dict = {
            "salt": encrypted.salt,
            "nonce": encrypted.nonce,
            "data": encrypted.data,
        }
        decrypted = decrypt_text(encrypted_dict, password)

        assert decrypted == original_text

    def test_wrong_password_fails(self):
        """测试错误密码失败"""
        original_text = "这是一段测试文本"
        correct_password = "correct_password"
        wrong_password = "wrong_password"

        # 使用正确密码加密
        encrypted = encrypt_text(original_text, correct_password, [])
        encrypted_dict = {
            "salt": encrypted.salt,
            "nonce": encrypted.nonce,
            "data": encrypted.data,
        }

        # 使用错误密码解密
        with pytest.raises(ValueError):
            decrypt_text(encrypted_dict, wrong_password)

    def test_different_salt_different_output(self):
        """测试不同盐值产生不同输出"""
        text = "测试文本"
        password = "test_password"

        encrypted1 = encrypt_text(text, password, [])
        encrypted2 = encrypt_text(text, password, [])

        # 两次加密的密文应该不同（因为随机盐值）
        assert encrypted1.data != encrypted2.data
        assert encrypted1.salt != encrypted2.salt
        assert encrypted1.nonce != encrypted2.nonce

    def test_encryption_result_structure(self):
        """测试加密结果结构"""
        text = "测试文本"
        password = "test_password"
        keywords = ["关键词1", "关键词2"]

        encrypted = encrypt_text(text, password, keywords)

        # 检查所有必需字段
        assert encrypted.salt is not None
        assert encrypted.nonce is not None
        assert encrypted.data is not None
        assert encrypted.created_at is not None
        assert encrypted.version == "2.0"
        assert encrypted.original_length == len(text)
        assert encrypted.masked_keywords == keywords

    def test_long_text_encryption(self):
        """测试长文本加密"""
        # 构造长文本（10000字符）
        long_text = "A" * 10000
        password = "test_password"

        encrypted = encrypt_text(long_text, password, [])
        encrypted_dict = {
            "salt": encrypted.salt,
            "nonce": encrypted.nonce,
            "data": encrypted.data,
        }
        decrypted = decrypt_text(encrypted_dict, password)

        assert decrypted == long_text

    def test_unicode_text_encryption(self):
        """测试Unicode文本加密"""
        unicode_text = "🔒 密文测试 🚀 Test 测试 العربية 日本語"
        password = "test_password_密码"

        encrypted = encrypt_text(unicode_text, password, [])
        encrypted_dict = {
            "salt": encrypted.salt,
            "nonce": encrypted.nonce,
            "data": encrypted.data,
        }
        decrypted = decrypt_text(encrypted_dict, password)

        assert decrypted == unicode_text

    def test_empty_payload_error(self):
        """测试空载荷错误"""
        with pytest.raises(ValueError):
            decrypt_text({}, "password")

    def test_malformed_payload_error(self):
        """测试畸形载荷错误"""
        payload = {
            "salt": "invalid_base64!",
            "nonce": "invalid_base64!",
            "data": "invalid_base64!"
        }

        with pytest.raises(ValueError):
            decrypt_text(payload, "password")

    def test_missing_fields_error(self):
        """测试缺少字段错误"""
        # 缺少 nonce
        payload = {
            "salt": "dGVzdHNhbHQ=",
            "data": "dGVzdGRhdGE="
        }

        with pytest.raises(ValueError):
            decrypt_text(payload, "password")


class TestKeyDerivation:
    """测试密钥派生功能"""

    def test_same_password_same_salt_same_key(self):
        """测试相同密码和盐值产生相同密钥"""
        password = "test_password"
        salt = b"test_salt_16byte"

        key1 = derive_key(password, salt)
        key2 = derive_key(password, salt)

        assert key1 == key2

    def test_different_passwords_different_keys(self):
        """测试不同密码产生不同密钥"""
        salt = b"test_salt_16byte"

        key1 = derive_key("password1", salt)
        key2 = derive_key("password2", salt)

        assert key1 != key2

    def test_different_salts_different_keys(self):
        """测试不同盐值产生不同密钥"""
        password = "test_password"

        key1 = derive_key(password, b"salt1_16byte____")
        key2 = derive_key(password, b"salt2_16byte____")

        assert key1 != key2

    def test_key_length(self):
        """测试密钥长度"""
        password = "test_password"
        salt = b"test_salt_16byte"

        key = derive_key(password, salt)

        # 应该是32字节（256位）
        assert len(key) == 32


class TestEncryptionIntegration:
    """加密解密集成测试"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 原始文本
        original = "客户张三，手机号13800138000，身份证110101199003071234"

        # 2. 加密
        password = "secure_password_123"
        encrypted = encrypt_text(original, password, ["张三"])

        # 3. 转换为字典（模拟保存）
        encrypted_dict = {
            "salt": encrypted.salt,
            "nonce": encrypted.nonce,
            "data": encrypted.data,
            "createdAt": encrypted.created_at,
            "version": encrypted.version
        }

        # 4. 模拟JSON序列化
        json_str = json.dumps(encrypted_dict)

        # 5. 模拟JSON反序列化
        loaded_dict = json.loads(json_str)

        # 6. 解密
        decrypted = decrypt_text(loaded_dict, password)

        # 7. 验证
        assert decrypted == original

    def test_chinese_password(self):
        """测试中文密码"""
        text = "测试文本"
        password = "密码测试123"

        encrypted = encrypt_text(text, password, [])
        encrypted_dict = {
            "salt": encrypted.salt,
            "nonce": encrypted.nonce,
            "data": encrypted.data,
        }
        decrypted = decrypt_text(encrypted_dict, password)

        assert decrypted == text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
