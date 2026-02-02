"""
脱敏功能单元测试
"""

import pytest
from app import normalize_keywords, mask_text_full, mask_text_partial, apply_smart_detection


class TestNormalizeKeywords:
    """测试关键词解析功能"""

    def test_empty_string(self):
        """测试空字符串"""
        assert normalize_keywords("") == []
        assert normalize_keywords(None) == []

    def test_single_keyword(self):
        """测试单个关键词"""
        result = normalize_keywords("张三")
        assert result == ["张三"]

    def test_comma_separated(self):
        """测试逗号分隔"""
        result = normalize_keywords("张三,李四,王五")
        assert result == ["张三", "李四", "王五"]

    def test_newline_separated(self):
        """测试换行分隔"""
        result = normalize_keywords("张三\n李四\n王五")
        assert result == ["张三", "李四", "王五"]

    def test_mixed_separators(self):
        """测试混合分隔符"""
        result = normalize_keywords("张三,李四\n王五；赵六")
        assert result == ["张三", "李四", "王五", "赵六"]

    def test_whitespace_trimming(self):
        """测试空白字符修剪"""
        result = normalize_keywords("张三 , 李四 , 王五")
        assert result == ["张三", "李四", "王五"]

    def test_empty_items_filtered(self):
        """测试过滤空项"""
        result = normalize_keywords("张三,,李四,\n,王五")
        assert result == ["张三", "李四", "王五"]


class TestMaskTextFull:
    """测试全量脱敏功能"""

    def test_basic_replacement(self):
        """测试基本替换"""
        result = mask_text_full("Hello 张三 World", "张三")
        assert result == "Hello *** World"

    def test_multiple_occurrences(self):
        """测试多次出现"""
        result = mask_text_full("张三说：张三来了", "张三")
        assert result == "***说：***来了"

    def test_special_characters(self):
        """测试特殊字符"""
        result = mask_text_full("Hello (test) World", "(test)")
        assert result == "Hello ****** World"

    def test_custom_mask_char(self):
        """测试自定义脱敏字符"""
        result = mask_text_full("Hello 张三 World", "张三", mask_char="#")
        assert result == "Hello ### World"

    def test_no_match(self):
        """测试无匹配"""
        result = mask_text_full("Hello World", "张三")
        assert result == "Hello World"


class TestMaskTextPartial:
    """测试部分脱敏功能"""

    def test_basic_partial(self):
        """测试基本部分脱敏"""
        result = mask_text_partial("Hello 张三 World", "张三", preserve_chars=1)
        assert result == "Hello 张** World"

    def test_preserve_multiple(self):
        """测试保留多个字符"""
        result = mask_text_partial("Hello 123456 World", "123456", preserve_chars=3)
        assert result == "Hello 123*** World"

    def test_short_text(self):
        """测试短文本（不脱敏）"""
        result = mask_text_partial("Hello 张 World", "张", preserve_chars=1)
        assert result == "Hello 张 World"

    def test_exact_length(self):
        """测试精确长度"""
        result = mask_text_partial("Hello 张三 World", "张三", preserve_chars=2)
        assert result == "Hello 张三 World"

    def test_custom_mask_char(self):
        """测试自定义脱敏字符"""
        result = mask_text_partial("Hello 张三 World", "张三", preserve_chars=1, mask_char="#")
        assert result == "Hello 张# World"


class TestSmartDetection:
    """测试智能识别功能"""

    def test_phone_detection(self):
        """测试手机号识别"""
        text = "我的手机号是13800138000"
        result, stats = apply_smart_detection(text)
        assert "手机号" in stats
        assert stats["手机号"] == 1
        assert "138******8000" in result

    def test_id_card_detection(self):
        """测试身份证号识别"""
        text = "身份证号：110101199003071234"
        result, stats = apply_smart_detection(text)
        assert "身份证号" in stats
        assert stats["身份证号"] == 1
        assert "110101************1234" in result

    def test_email_detection(self):
        """测试邮箱识别"""
        text = "邮箱：zhangsan@example.com"
        result, stats = apply_smart_detection(text)
        assert "邮箱" in stats
        assert stats["邮箱"] == 1
        assert "zh***************" in result

    def test_bank_card_detection(self):
        """测试银行卡号识别"""
        text = "银行卡号：6222021234567890123"
        result, stats = apply_smart_detection(text)
        assert "银行卡号" in stats
        assert stats["银行卡号"] == 1
        assert "6222*************" in result

    def test_ip_detection(self):
        """测试IP地址识别"""
        text = "IP地址：192.168.1.1"
        result, stats = apply_smart_detection(text)
        assert "IP地址" in stats
        assert stats["IP地址"] == 1
        assert "192.***.*.*" in result

    def test_multiple_detections(self):
        """测试多种类型同时检测"""
        text = """
        手机号：13800138000
        身份证：110101199003071234
        邮箱：test@example.com
        """
        result, stats = apply_smart_detection(text)
        assert len(stats) == 3
        assert stats["手机号"] == 1
        assert stats["身份证号"] == 1
        assert stats["邮箱"] == 1

    def test_no_detection(self):
        """测试无敏感信息"""
        text = "这是一段普通文本"
        result, stats = apply_smart_detection(text)
        assert len(stats) == 0
        assert result == text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
