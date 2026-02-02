"""
自定义脱敏工具 - 核心功能模块
提供脱敏、加密解密、文件处理等核心功能
"""

from .masking import (
    normalize_keywords,
    mask_text_full,
    mask_text_partial,
    apply_smart_detection,
    build_masked_text,
    PREDEFINED_PATTERNS,
)
from .encryption import derive_key, encrypt_text, decrypt_text
from .file_handler import (
    extract_file_text,
    load_docx_text,
    load_pdf_text,
    build_docx_bytes,
    build_zip_bundle,
)
from .enhanced_doc import (
    extract_docx_with_format,
    build_docx_with_format,
    mask_paragraphs_data,
)
from .ooxml_processor import (
    apply_ooxml_masking,
    OOXMLProcessor,
)

__all__ = [
    # 脱敏相关
    "normalize_keywords",
    "mask_text_full",
    "mask_text_partial",
    "apply_smart_detection",
    "build_masked_text",
    "PREDEFINED_PATTERNS",
    # 加密解密
    "derive_key",
    "encrypt_text",
    "decrypt_text",
    # 文件处理
    "extract_file_text",
    "load_docx_text",
    "load_pdf_text",
    "build_docx_bytes",
    "build_zip_bundle",
    # 增强文档处理
    "extract_docx_with_format",
    "build_docx_with_format",
    "mask_paragraphs_data",
    # OOXML 高级处理
    "apply_ooxml_masking",
    "OOXMLProcessor",
]
