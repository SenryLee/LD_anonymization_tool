# 智能文本脱敏 · 本地加密还原 · 专业级文档处理
# 🔒 脱敏工具

> 一个功能强大、安全可靠的文本脱敏工具，支持 Word、PDF、TXT 文件的智能脱敏处理。所有处理均在本地完成，确保数据隐私安全。

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-lightgrey)](https://github.com/your-repo)

---

## ✨ 核心功能

### 🎯 多种脱敏模式
- **全量替换**：完全隐藏敏感内容（如：张三 → ***）
- **部分遮蔽**：保留前几位，其余隐藏（如：张三 → 张*）
- **智能识别**：自动识别并脱敏常见敏感信息

### 🤖 智能识别（10种）

自动识别并脱敏以下类型的敏感信息：

- 📱 **手机号** - 保留前3位
- 🪪 **身份证号** - 保留前6位
- 📧 **邮箱地址** - 保留前2位
- 💳 **银行卡号** - 保留前4位
- 🌐 **IP地址** - 保留前4位
- 🏢 **企业名称** - 保留法律后缀（如"有限公司"）
- 🏠 **详细地址** - 保留前3位
- 🚗 **车牌号** - 保留前2位
- 🔢 **统一社会信用代码** - 保留前4位
- 💰 **金额** - 完全脱敏（支持¥/$/USD等符号）

### 🧬 OOXML 深度处理（DOCX专用）

- ✅ **Run级处理**：解决字符碎片化问题
- ✅ **格式保持**：完美保持原有样式、字号、颜色
- ✅ **布局稳定**：使用等长占位符，避免排版错乱
- ✅ **完整遍历**：支持正文、表格、页眉、页脚、嵌套表格

### 🔐 军国级加密

- **AES-256-GCM** 加密算法
- **PBKDF2** 密码钥派生（120,000 次迭代）
- 随机盐值和 Nonce（每次加密唯一）
- 密码强度验证（至少6位）

### 📄 多格式支持

- **输入格式**：TXT、DOCX、PDF
- **输出格式**：DOCX（脱敏文档）、JSON（加密还原文件）
- **文件大小**：最大支持 50MB

---

## 🚀 快速开始

### 方式一：桌面应用（推荐）⭐

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/desensitization-tool.git
cd desensitization-tool/source

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行应用
python desktop_app.py
```

### 方式二：Streamlit 应用

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
streamlit run app.py

# 3. 打开浏览器
# 访问 http://localhost:8501
```

### 方式三：纯 HTML 版本

直接在浏览器中打开 `index.html` 即可使用，无需安装任何依赖。

---

## 📦 打包发布

### macOS

```bash
# 1. 安装打包工具
pip install pyinstaller

# 2. 执行打包
python build.py

# 3. 生成的文件
# dist/脱敏工具.app
```

### Windows

```cmd
# 1. 安装打包工具
pip install pyinstaller

# 2. 执行打包
python build.py

# 3. 生成的文件
# dist\脱敏工具.exe
```

详细打包说明请参考：[BUILD_README.md](../docs/BUILD_README.md)

---

## 📖 使用指南

### 脱敏流程

1. **上传文件**：选择 TXT、DOCX 或 PDF 文件
2. **设置关键词**：输入需要脱敏的关键词（可选）
3. **启用智能识别**：勾选自动识别敏感信息
4. **OOXML 深度处理**：DOCX 文档推荐启用（保持格式）
5. **设置密码**：设置还原密码（至少6位）
6. **开始脱敏**：点击按钮开始处理
7. **下载文件**：获取脱敏文档和加密还原文件

### 还原流程

1. **上传加密文件**：选择 `.json` 还原文件
2. **输入密码**：输入之前设置的还原密码
3. **解密还原**：点击解密按钮
4. **下载原文**：获取原始文档

---

## 🛠️ 技术栈

- **UI 框架**：CustomTkinter 5.2.1
- **文档处理**：python-docx, pdfplumber
- **加密**：cryptography (AES-256-GCM)
- **正则表达式**：re (Python 标准库)
- **打包工具**：PyInstaller

---

## 📁 项目结构

```
source/
├── core/                      # 核心模块
│   ├── __init__.py
│   ├── masking.py             # 脱敏功能
│   ├── encryption.py          # 加密解密
│   ├── file_handler.py        # 文件处理
│   ├── enhanced_doc.py        # 格式保持
│   └── ooxml_processor.py     # OOXML深度处理
├── desktop_app.py             # 桌面应用主程序
├── app.py                     # Streamlit版本
├── index.html                 # 纯HTML版本
├── requirements.txt           # Python依赖
├── tests/                     # 测试文件
└── README.md                  # 本文件
```

---

## 🧪 运行测试

```bash
# 安装测试依赖
pip install pytest

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_masking.py
pytest tests/test_encryption.py
```

---

## ⚙️ 配置说明

### 脱敏模式

- **FULL**：全量替换（张三 → ***）
- **PARTIAL**：部分遮蔽（张三 → 张*，可自定义保留位数）
- **REGEX**：正则匹配
- **SMART**：智能识别

### 智能识别开关

在 `core/masking.py` 中的 `PREDEFINED_PATTERNS` 可以自定义识别模式：

```python
PREDEFINED_PATTERNS = {
    "手机号": MaskPattern(...),
    "身份证号": MaskPattern(...),
    # ... 更多模式
}
```

---

## 🔒 安全特性

- ✅ **本地处理**：所有操作在本地完成，数据不上传
- ✅ **强加密**：AES-256-GCM 认证加密
- ✅ **密钥派生**：PBKDF2 (120,000 次迭代)
- ✅ **随机盐值**：每次加密使用唯一盐值
- ✅ **密码验证**：强制至少6位密码
- ✅ **无网络请求**：不包含任何网络通信代码

---

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 👨‍💻 作者

- **开发者**：[您的名字]
- **项目链接**：[https://github.com/your-username/desensitization-tool](https://github.com/your-username/desensitization-tool)

---

## 🙏 致谢

感谢以下开源项目：

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化 UI 框架
- [python-docx](https://python-docx.readthedocs.io/) - Word 文档处理
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF 文档处理
- [cryptography](https://github.com/pyca/cryptography) - 加密库

---

## 📮 联系方式

- **问题反馈**：[GitHub Issues](https://github.com/your-username/desensitization-tool/issues)
- **邮件**：[your-email@example.com]

---

**⭐ 如果这个项目对您有帮助，请给个 Star！**
