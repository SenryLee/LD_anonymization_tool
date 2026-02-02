"""
脱敏功能模块
提供文本脱敏的核心功能
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict


class MaskMode(Enum):
    """脱敏模式枚举"""
    FULL = "full"  # 全量替换：张三 -> ***
    PARTIAL = "partial"  # 部分遮蔽：张三 -> 张*
    REGEX = "regex"  # 正则匹配
    SMART = "smart"  # 智能识别


@dataclass
class MaskPattern:
    """脱敏模式配置"""
    name: str
    pattern: str
    mode: MaskMode
    preserve_chars: int = 0
    mask_char: str = "*"
    description: str = ""


# 预定义脱敏模式
PREDEFINED_PATTERNS: Dict[str, MaskPattern] = {
    "手机号": MaskPattern(
        name="手机号",
        pattern=r"1[3-9]\d{9}",
        mode=MaskMode.PARTIAL,
        preserve_chars=3,
        mask_char="*",
        description="中国大陆手机号，保留前3位"
    ),
    "身份证号": MaskPattern(
        name="身份证号",
        pattern=r"[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]",
        mode=MaskMode.PARTIAL,
        preserve_chars=6,
        mask_char="*",
        description="18位身份证号，保留前6位"
    ),
    "邮箱": MaskPattern(
        name="邮箱",
        pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        mode=MaskMode.PARTIAL,
        preserve_chars=2,
        mask_char="*",
        description="电子邮箱地址，保留前2位"
    ),
    "银行卡号": MaskPattern(
        name="银行卡号",
        pattern=r"\b\d{16,19}\b",
        mode=MaskMode.PARTIAL,
        preserve_chars=4,
        mask_char="*",
        description="银行卡号，保留前4位"
    ),
    "IP地址": MaskPattern(
        name="IP地址",
        pattern=r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        mode=MaskMode.PARTIAL,
        preserve_chars=4,
        mask_char="*",
        description="IPv4地址"
    ),
    "统一社会信用代码": MaskPattern(
        name="统一社会信用代码",
        pattern=r"[0-9A-HJ-NPQRTUW-Y]{2}\d{6}[0-9A-HJ-NPQRTUW-Y]{10}",
        mode=MaskMode.PARTIAL,
        preserve_chars=4,
        mask_char="*",
        description="18位统一社会信用代码，保留前4位"
    ),
    "企业名称": MaskPattern(
        name="企业名称",
        pattern=r"[\u4e00-\u9fa5]{2,10}(?:有限公司|股份有限公司|有限责任公司|集团|公司|企业|厂|店|行|中心|工作室|合伙企业|控股|科技|网络|信息|技术|贸易|商贸|实业|发展|建设|投资|管理|咨询|服务|教育|文化|传媒|电子|汽车|房地产|能源|化工|制造|物流|运输|建筑|装饰|设计|广告|餐饮|酒店|医院|学校|银行|保险|证券|基金)",
        mode=MaskMode.PARTIAL,
        preserve_chars=0,  # 保留0位，完全脱敏公司名称
        mask_char="*",
        description="企业名称，完全脱敏公司名称，保留后缀"
    ),
    "详细地址": MaskPattern(
        name="详细地址",
        pattern=r"[\u4e00-\u9fa5]{2,6}(?:省|市|区|县|镇|乡|街道|路|巷|号|栋|单元|楼|层|室|户)[\u4e00-\u9fa5\d\w\-#号]*",
        mode=MaskMode.PARTIAL,
        preserve_chars=3,
        mask_char="*",
        description="详细地址，保留前3位"
    ),
    "车牌号": MaskPattern(
        name="车牌号",
        pattern=r"[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-Z0-9]{5,6}",
        mode=MaskMode.PARTIAL,
        preserve_chars=2,
        mask_char="*",
        description="中国车牌号，保留前2位"
    ),
    "金额": MaskPattern(
        name="金额",
        pattern=r"(?:¥|￥|USD?|\$)\s*(?:\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)\s*(?:万元?|元)?|(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?\s*(?:万元?|元)",
        mode=MaskMode.PARTIAL,
        preserve_chars=0,  # 金额完全脱敏
        mask_char="*",
        description="金额数字，支持¥/$/USD等货币符号和千分位格式"
    ),
}


def normalize_keywords(raw: str) -> list:
    """解析关键词列表，支持换行、逗号、分号分隔"""
    if not raw:
        return []
    return [item.strip() for item in re.split(r"[\n,;，；]", raw) if item.strip()]


def mask_text_full(text: str, keyword: str, mask_char: str = "*") -> str:
    """全量替换模式"""
    escaped = re.escape(keyword)
    return re.sub(escaped, mask_char * len(keyword), text)


def mask_text_partial(text: str, keyword: str, preserve_chars: int = 1, mask_char: str = "*") -> str:
    """部分遮蔽模式：保留前N位，其余用*替换"""
    escaped = re.escape(keyword)

    def replacement(match):
        original = match.group(0)
        if len(original) <= preserve_chars:
            return original
        return original[:preserve_chars] + mask_char * (len(original) - preserve_chars)

    return re.sub(escaped, replacement, text)


def mask_text_regex(text: str, pattern: str, preserve_chars: int = 0, mask_char: str = "*") -> tuple:
    """正则匹配模式"""
    match_count = 0

    def replacement(match):
        nonlocal match_count
        match_count += 1
        original = match.group(0)

        # 特殊处理：企业名称脱敏，保留后缀
        if preserve_chars == 0 and "公司" in original or "企业" in original:
            # 找到后缀位置
            suffixes = [
                "股份有限公司", "有限公司", "有限责任公司",
                "集团有限公司", "公司", "企业", "集团"
            ]

            for suffix in suffixes:
                if original.endswith(suffix):
                    # 只脱敏公司名称部分，保留后缀
                    name_part = original[:-len(suffix)]
                    suffix_part = suffix
                    return mask_char * len(name_part) + suffix_part

        # 普通处理
        if len(original) <= preserve_chars:
            return original
        return original[:preserve_chars] + mask_char * (len(original) - preserve_chars)

    masked = re.sub(pattern, replacement, text)
    return masked, match_count


def apply_smart_detection(text: str) -> tuple:
    """智能识别常见敏感信息并脱敏"""
    stats = {}
    result = text

    for name, pattern in PREDEFINED_PATTERNS.items():
        result, count = mask_text_regex(
            result,
            pattern.pattern,
            pattern.preserve_chars,
            pattern.mask_char
        )
        if count > 0:
            stats[name] = count

    return result, stats


def build_masked_text(
    text: str,
    keywords: list,
    mask_mode: MaskMode = MaskMode.FULL,
    preserve_chars: int = 1,
    mask_char: str = "*",
    enable_smart: bool = False
) -> tuple:
    """构建脱敏文本"""
    masked = text
    stats = {"manual_keywords": len(keywords), "smart_detection": {}}

    # 应用手动关键词脱敏
    if keywords:
        if mask_mode == MaskMode.FULL:
            for word in keywords:
                masked = mask_text_full(masked, word, mask_char)
        elif mask_mode == MaskMode.PARTIAL:
            for word in keywords:
                masked = mask_text_partial(masked, word, preserve_chars, mask_char)

    # 应用智能识别
    if enable_smart:
        masked, smart_stats = apply_smart_detection(masked)
        stats["smart_detection"] = smart_stats

    return masked, stats
