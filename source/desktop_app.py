"""
自定义脱敏工具 - CustomTkinter 桌面版
本地安全处理，支持文件脱敏和加密还原
"""

import os
import threading
from dataclasses import asdict
from datetime import datetime
from tkinter import filedialog

import customtkinter as ctk

# 导入核心功能模块
from core.masking import (
    MaskMode,
    normalize_keywords,
    build_masked_text,
)
from core.encryption import encrypt_text, decrypt_text
from core.file_handler import (
    extract_file_text,
    build_docx_bytes,
    build_zip_bundle,
)
from core.enhanced_doc import (
    extract_docx_with_format,
    build_docx_with_format,
    mask_paragraphs_data,
)
from core.ooxml_processor import apply_ooxml_masking

try:
    from CTkMessagebox import CTkMessagebox
except ImportError:
    # 如果未安装 CTkMessagebox，使用默认的 messagebox
    from tkinter import messagebox as TkMessagebox

    class CTkMessagebox:
        @staticmethod
        def show_error(parent, title, message):
            TkMessagebox.showerror(title, message)

        @staticmethod
        def show_success(parent, title, message):
            TkMessagebox.showinfo(title, message)

        @staticmethod
        def show_warning(parent, title, message):
            TkMessagebox.showwarning(title, message)


class MaskingApp(ctk.CTk):
    """脱敏工具主窗口类"""

    def __init__(self):
        super().__init__()

        # 配置窗口
        self.title("定义词脱敏工具 - 本地安全处理")
        self.geometry("1400x800")
        self.minsize(1200, 700)

        # 设置深色主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # 初始化数据
        self.current_file = None
        self.current_text = None
        self.current_paragraphs = None  # 新增：存储格式化的段落数据
        self.processing = False
        self.mask_mode = MaskMode.FULL
        self.preserve_chars = 1
        self.bundle_bytes = None
        self.use_enhanced_format = True  # 新增：是否使用增强格式处理

        # 构建UI
        self.setup_ui()

    def setup_ui(self):
        """构建UI界面"""
        # 顶部标题栏
        header = self.create_header()
        header.pack(fill="x", padx=20, pady=(20, 10))

        # 主内容区（三列布局）
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # 配置网格列权重
        main_content.grid_columnconfigure((0, 1, 2), weight=1)
        main_content.grid_rowconfigure(0, weight=1)

        # 左列：文件上传 + 配置
        left_column = self.create_left_column(main_content)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 中列：处理结果 + 统计
        center_column = self.create_center_column(main_content)
        center_column.grid(row=0, column=1, sticky="nsew", padx=5)

        # 右列：还原解密
        right_column = self.create_right_column(main_content)
        right_column.grid(row=0, column=2, sticky="nsew", padx=(5, 0))

    def create_header(self):
        """创建顶部标题栏"""
        header = ctk.CTkFrame(self, height=80)
        header.pack_propagate(False)

        # 标题
        title_label = ctk.CTkLabel(
            header,
            text="🔒 定义词脱敏工具",
            font=("Arial", 28, "bold"),
            text_color=("#1f5f9b", "#818cf8")
        )
        title_label.pack(pady=(15, 5))

        # 副标题
        subtitle_label = ctk.CTkLabel(
            header,
            text="智能文本脱敏 · 本地加密还原 · 数据不离开您的设备",
            font=("Arial", 14),
            text_color="gray"
        )
        subtitle_label.pack()

        return header

    def create_left_column(self, parent):
        """创建左列面板"""
        column = ctk.CTkScrollableFrame(parent, label_text="📝 文本脱敏")
        column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # 文件上传区域
        self.create_file_upload_area(column)

        # 关键词输入
        self.create_keywords_area(column)

        # 高级选项
        self.create_advanced_options(column)

        # 密码输入
        self.create_password_area(column)

        # 开始按钮
        self.mask_button = ctk.CTkButton(
            column,
            text="🚀 开始脱敏",
            font=("Arial", 16, "bold"),
            height=45,
            command=self.on_mask_button_click
        )
        self.mask_button.pack(fill="x", padx=15, pady=15)

        # 状态提示
        self.mask_status = ctk.CTkLabel(
            column,
            text="等待上传文件...",
            font=("Arial", 12),
            text_color="gray"
        )
        self.mask_status.pack(pady=(0, 15))

        return column

    def create_file_upload_area(self, parent):
        """创建文件上传区域"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.pack(fill="x", padx=15, pady=10)

        # 标题
        title = ctk.CTkLabel(
            frame,
            text="📁 文件上传",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        title.pack(fill="x", padx=15, pady=(15, 10))

        # 上传按钮
        upload_btn = ctk.CTkButton(
            frame,
            text="点击选择文件",
            font=("Arial", 13),
            height=40,
            command=self.on_file_click
        )
        upload_btn.pack(fill="x", padx=15, pady=(0, 10))

        # 文件信息
        self.file_info_label = ctk.CTkLabel(
            frame,
            text="未选择文件",
            font=("Arial", 11),
            text_color="gray"
        )
        self.file_info_label.pack(padx=15, pady=(0, 15))

    def create_keywords_area(self, parent):
        """创建关键词输入区域"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.pack(fill="x", padx=15, pady=10)

        # 标题
        title = ctk.CTkLabel(
            frame,
            text="🔑 脱敏关键词",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        title.pack(fill="x", padx=15, pady=(15, 10))

        # 输入框
        self.keywords_input = ctk.CTkTextbox(
            frame,
            height=80,
            font=("Arial", 12)
        )
        self.keywords_input.pack(fill="x", padx=15, pady=(0, 5))

        # 提示
        hint = ctk.CTkLabel(
            frame,
            text="支持换行、逗号、分号分隔",
            font=("Arial", 10),
            text_color="gray"
        )
        hint.pack(padx=15, pady=(0, 15))

    def create_advanced_options(self, parent):
        """创建高级选项区域"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.pack(fill="x", padx=15, pady=10)

        # 标题
        title = ctk.CTkLabel(
            frame,
            text="⚙️ 高级选项",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        title.pack(fill="x", padx=15, pady=(15, 10))

        # 脱敏模式
        mode_frame = ctk.CTkFrame(frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=15, pady=(0, 10))

        mode_label = ctk.CTkLabel(
            mode_frame,
            text="脱敏模式：",
            font=("Arial", 11),
            width=80,
            anchor="w"
        )
        mode_label.pack(side="left", padx=(0, 10))

        self.mask_mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=["全量替换", "部分遮蔽"],
            command=self.on_mask_mode_change
        )
        self.mask_mode_menu.pack(side="left", fill="x", expand=True)

        # 保留字符数（初始隐藏）
        self.preserve_frame = ctk.CTkFrame(frame, fg_color="transparent")
        # 不pack，等用户选择部分遮蔽模式时才显示

        # 智能识别
        self.smart_detect = ctk.BooleanVar(value=False)
        smart_checkbox = ctk.CTkCheckBox(
            frame,
            text="🤖 启用智能识别（手机号、身份证、邮箱、企业名称、信用代码、地址、金额等）",
            variable=self.smart_detect,
            font=("Arial", 11)
        )
        smart_checkbox.pack(padx=15, pady=(0, 8))

        # OOXML 深度处理（仅对 DOCX 有效）
        self.use_ooxml = ctk.BooleanVar(value=False)
        ooxml_checkbox = ctk.CTkCheckBox(
            frame,
            text="🧬 启用 OOXML 深度处理（保持样式、等长占位，避免字符碎片）",
            variable=self.use_ooxml,
            font=("Arial", 11)
        )
        ooxml_checkbox.pack(padx=15, pady=(0, 8))

        # 提示信息
        ooxml_hint = ctk.CTkLabel(
            frame,
            text="💡 仅适用于 DOCX 文件，可在字符级别保持样式和布局",
            font=("Arial", 9),
            text_color="gray",
            anchor="w"
        )
        ooxml_hint.pack(padx=15, pady=(0, 15))

    def create_password_area(self, parent):
        """创建密码输入区域"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.pack(fill="x", padx=15, pady=10)

        # 标题
        title = ctk.CTkLabel(
            frame,
            text="🔐 还原密码",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        title.pack(fill="x", padx=15, pady=(15, 10))

        # 输入框
        self.password_input = ctk.CTkEntry(
            frame,
            placeholder_text="⚠️ 必须设置至少6位密码！例如：123456",
            show="*",
            height=40
        )
        self.password_input.pack(fill="x", padx=15, pady=(0, 5))

        # 密码提示标签
        password_hint = ctk.CTkLabel(
            frame,
            text="⚠️ 重要：请务必设置6位以上密码，否则无法开始脱敏！",
            font=("Arial", 10),
            text_color="#ff6b6b",
            anchor="w"
        )
        password_hint.pack(fill="x", padx=15, pady=(0, 15))

    def create_center_column(self, parent):
        """创建中列面板"""
        column = ctk.CTkFrame(parent)
        column.pack_propagate(False)

        # 标题
        title = ctk.CTkLabel(
            column,
            text="📦 脱敏结果",
            font=("Arial", 20, "bold"),
            anchor="w"
        )
        title.pack(fill="x", padx=15, pady=(15, 10))

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(column)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 15))

        # 统计卡片区域
        self.stats_frame = ctk.CTkFrame(column)
        self.stats_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.create_stat_cards()

        # 预览区域
        preview_label = ctk.CTkLabel(
            column,
            text="👁️ 结果预览（前500字符）",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        preview_label.pack(fill="x", padx=15, pady=(0, 10))

        self.result_preview = ctk.CTkTextbox(
            column,
            height=250,
            font=("Consolas", 11)
        )
        self.result_preview.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.result_preview.insert("1.0", "脱敏完成后将在此显示预览...")
        self.result_preview.configure(state="disabled")

        # 下载按钮
        self.download_button = ctk.CTkButton(
            column,
            text="📥 下载脱敏包",
            font=("Arial", 14, "bold"),
            height=40,
            state="disabled",
            command=self.on_download_click
        )
        self.download_button.pack(fill="x", padx=15, pady=(0, 15))

        return column

    def create_stat_cards(self):
        """创建统计卡片"""
        # 清空现有内容
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # 3列布局，两行
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.stats_frame.grid_rowconfigure((0, 1), weight=1)

        self.stat_labels = {}

        stats_config = [
            ("keywords", "关键词", "0"),
            ("phone", "手机号", "0"),
            ("idcard", "身份证", "0"),
            ("email", "邮箱", "0"),
            ("credit_code", "信用代码", "0"),
            ("company", "企业名", "0"),
            ("address", "地址", "0"),
            ("bank_card", "银行卡", "0"),
            ("license_plate", "车牌号", "0"),
            ("amount", "金额", "0"),
        ]

        for i, (key, label_text, default) in enumerate(stats_config):
            row = i // 3
            col = i % 3

            card = ctk.CTkFrame(self.stats_frame)
            card.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

            value_label = ctk.CTkLabel(
                card,
                text=default,
                font=("Arial", 20, "bold"),
                text_color=("#1f5f9b", "#818cf8")
            )
            value_label.pack(pady=(10, 3))

            name_label = ctk.CTkLabel(
                card,
                text=label_text,
                font=("Arial", 10),
                text_color="gray"
            )
            name_label.pack(pady=(0, 10))

            self.stat_labels[key] = value_label

    def create_right_column(self, parent):
        """创建右列面板"""
        column = ctk.CTkFrame(parent)
        column.pack_propagate(False)

        # 标题
        title = ctk.CTkLabel(
            column,
            text="🔓 还原原文",
            font=("Arial", 20, "bold"),
            anchor="w"
        )
        title.pack(fill="x", padx=15, pady=(15, 10))

        # 文件上传
        frame = ctk.CTkFrame(column, corner_radius=10)
        frame.pack(fill="x", padx=15, pady=10)

        upload_title = ctk.CTkLabel(
            frame,
            text="📁 选择加密文件",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        upload_title.pack(fill="x", padx=15, pady=(15, 10))

        self.restore_upload_btn = ctk.CTkButton(
            frame,
            text="点击选择 JSON 文件",
            font=("Arial", 13),
            height=40,
            command=self.on_restore_file_click
        )
        self.restore_upload_btn.pack(fill="x", padx=15, pady=(0, 10))

        self.restore_file_label = ctk.CTkLabel(
            frame,
            text="未选择文件",
            font=("Arial", 11),
            text_color="gray"
        )
        self.restore_file_label.pack(padx=15, pady=(0, 15))

        # 密码输入
        password_frame = ctk.CTkFrame(column, corner_radius=10)
        password_frame.pack(fill="x", padx=15, pady=10)

        password_title = ctk.CTkLabel(
            password_frame,
            text="🔑 还原密码",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        password_title.pack(fill="x", padx=15, pady=(15, 10))

        self.restore_password_input = ctk.CTkEntry(
            password_frame,
            placeholder_text="输入生成时设置的密码",
            show="*",
            height=40
        )
        self.restore_password_input.pack(fill="x", padx=15, pady=(0, 15))

        # 解密按钮
        self.restore_button = ctk.CTkButton(
            column,
            text="🔓 解密并下载原文",
            font=("Arial", 14, "bold"),
            height=45,
            command=self.on_restore_click
        )
        self.restore_button.pack(fill="x", padx=15, pady=15)

        # 状态提示
        self.restore_status = ctk.CTkLabel(
            column,
            text="等待加密文件...",
            font=("Arial", 12),
            text_color="gray",
            wraplength=300
        )
        self.restore_status.pack(pady=(0, 15))

        return column

    # ==================== 事件处理 ====================

    def on_file_click(self):
        """处理文件选择点击"""
        file_path = filedialog.askopenfilename(
            title="选择文件",
            filetypes=[
                ("支持的文件", "*.txt *.docx *.pdf"),
                ("文本文件", "*.txt"),
                ("Word文档", "*.docx"),
                ("PDF文档", "*.pdf"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.process_uploaded_file(file_path)

    def process_uploaded_file(self, file_path):
        """处理上传的文件"""
        try:
            # 显示加载状态
            self.mask_status.configure(
                text=f"⏳ 正在读取: {os.path.basename(file_path)}...",
                text_color="yellow"
            )
            self.update()

            # 在后台线程读取文件
            def read_file():
                try:
                    with open(file_path, 'rb') as f:
                        # 判断文件类型
                        if file_path.lower().endswith('.docx'):
                            # 使用增强格式提取
                            paragraphs_data = extract_docx_with_format(f)
                            text = "\n".join([p.text for p in paragraphs_data])
                            self.after(0, lambda: self.on_file_loaded_with_format(text, file_path, paragraphs_data))
                        else:
                            # 普通文本提取
                            text = extract_file_text(f)
                            self.after(0, lambda: self.on_file_loaded(text, file_path))
                except Exception as e:
                    self.after(0, lambda: self.on_file_error(str(e)))

            threading.Thread(target=read_file, daemon=True).start()

        except Exception as e:
            self.on_file_error(str(e))

    def on_file_loaded(self, text, file_path):
        """文件加载完成回调（纯文本模式）"""
        self.current_text = text
        self.current_file = file_path
        self.current_paragraphs = None

        # 更新文件信息显示
        file_size = os.path.getsize(file_path) / 1024  # KB
        self.file_info_label.configure(
            text=f"✅ {os.path.basename(file_path)} ({file_size:.1f} KB)",
            text_color="#34d399"
        )

        self.mask_status.configure(
            text=f"✅ 已读取文件 ({len(text)} 字符)",
            text_color="#34d399"
        )

    def on_file_loaded_with_format(self, text, file_path, paragraphs_data):
        """文件加载完成回调（增强格式模式）"""
        self.current_text = text
        self.current_file = file_path
        self.current_paragraphs = paragraphs_data

        # 更新文件信息显示
        file_size = os.path.getsize(file_path) / 1024  # KB
        self.file_info_label.configure(
            text=f"✅ {os.path.basename(file_path)} ({file_size:.1f} KB)",
            text_color="#34d399"
        )

        format_info = " (保持格式)" if self.use_enhanced_format else ""
        self.mask_status.configure(
            text=f"✅ 已读取文件 ({len(text)} 字符{format_info})",
            text_color="#34d399"
        )

    def on_file_error(self, error_msg):
        """文件加载错误回调"""
        self.file_info_label.configure(
            text=f"❌ 读取失败",
            text_color="red"
        )
        self.mask_status.configure(
            text=f"❌ {error_msg}",
            text_color="red"
        )
        CTkMessagebox.show_error(self, "读取失败", error_msg)

    def on_mask_mode_change(self, choice):
        """脱敏模式改变"""
        if choice == "全量替换":
            self.mask_mode = MaskMode.FULL
            # 隐藏保留字符数选项
            self.preserve_frame.pack_forget()
        else:
            self.mask_mode = MaskMode.PARTIAL
            # 显示保留字符数选项
            self.show_preserve_chars_option()

    def show_preserve_chars_option(self):
        """显示保留字符数选项"""
        # 清空并重建
        for widget in self.preserve_frame.winfo_children():
            widget.destroy()

        self.preserve_frame.pack(fill="x", padx=15, pady=(0, 10))

        label = ctk.CTkLabel(
            self.preserve_frame,
            text="保留字符数：",
            font=("Arial", 11),
            width=80,
            anchor="w"
        )
        label.pack(side="left", padx=(0, 10))

        self.preserve_slider = ctk.CTkSlider(
            self.preserve_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            command=self.on_preserve_chars_change
        )
        self.preserve_slider.set(1)
        self.preserve_slider.pack(side="left", fill="x", expand=True)

        self.preserve_value_label = ctk.CTkLabel(
            self.preserve_frame,
            text="1",
            font=("Arial", 11),
            width=30
        )
        self.preserve_value_label.pack(side="left", padx=(10, 0))

    def on_preserve_chars_change(self, value):
        """保留字符数改变"""
        self.preserve_chars = int(value)
        if hasattr(self, 'preserve_value_label'):
            self.preserve_value_label.configure(text=str(int(value)))

    def on_mask_button_click(self):
        """处理脱敏按钮点击"""
        if self.processing:
            return

        # 验证输入
        if not self.current_text:
            CTkMessagebox.show_error(self, "错误", "请先上传文件")
            return

        keywords_str = self.keywords_input.get("1.0", "end-1c")
        keywords = normalize_keywords(keywords_str)

        if not keywords and not self.smart_detect.get():
            CTkMessagebox.show_error(
                self, "错误", "请输入关键词或启用智能识别"
            )
            return

        password = self.password_input.get()
        if not password:
            CTkMessagebox.show_error(self, "错误", "请设置还原密码")
            return

        if len(password) < 6:
            CTkMessagebox.show_error(self, "错误", "密码长度至少6位")
            return

        # 开始异步处理
        self.processing = True
        self.mask_button.configure(state="disabled", text="⏳ 处理中...")
        self.progress_bar.set(0)
        self.mask_status.configure(text="⏳ 处理中...", text_color="yellow")

        # 在后台线程执行脱敏
        def process_masking():
            try:
                # 更新进度
                self.after(0, lambda: self.progress_bar.set(0.2))

                # 检查是否使用 OOXML 深度处理
                use_ooxml_processing = (
                    self.use_ooxml.get() and
                    self.current_file and
                    self.current_file.lower().endswith('.docx')
                )

                if use_ooxml_processing:
                    # 使用 OOXML 深度处理（直接在 Word 文档结构上操作）
                    self.after(0, lambda: self.progress_bar.set(0.3))

                    # 构建 mask_patterns（从智能识别模式构建）
                    mask_patterns = {}
                    if self.smart_detect.get():
                        from core.masking import PREDEFINED_PATTERNS
                        for name, pattern in PREDEFINED_PATTERNS.items():
                            mask_patterns[name] = pattern.pattern

                    # 应用 OOXML 级别的脱敏
                    import io
                    with open(self.current_file, 'rb') as f:
                        file_content = io.BytesIO(f.read())
                        file_content.seek(0)
                        masked_docx = apply_ooxml_masking(
                            file_content,
                            keywords,
                            mask_patterns,
                            preserve_suffix=True
                        )

                    self.after(0, lambda: self.progress_bar.set(0.6))

                    # 为了统计和预览，仍需提取文本
                    from core.file_handler import load_docx_text
                    masked_io = io.BytesIO(masked_docx)
                    masked = load_docx_text(masked_io)

                    # 计算统计信息（简化版）
                    stats = {
                        "manual_keywords": len(keywords),
                        "smart_detection": {}
                    }
                    if self.smart_detect.get():
                        # 这里可以添加更精确的统计逻辑
                        stats["smart_detection"] = {
                            "手机号": masked.count("█") // 11,
                            "其他": "已处理"
                        }

                    # 加密原文
                    encrypted = encrypt_text(self.current_text, password, keywords)
                    encrypted_dict = asdict(encrypted)
                    encrypted_dict['created_at'] = datetime.now().isoformat(timespec="seconds")

                    self.after(0, lambda: self.progress_bar.set(0.9))

                    # 生成文件名（使用原始文件名+脱敏文件）
                    original_filename = os.path.splitext(os.path.basename(self.current_file))[0]
                    stamp = f"{original_filename}_脱敏文件"
                    bundle_bytes = build_zip_bundle(masked_docx, encrypted_dict, stamp)

                else:
                    # 使用原有的文本处理流程
                    # 执行脱敏
                    masked, stats = build_masked_text(
                        self.current_text,
                        keywords,
                        self.mask_mode,
                        self.preserve_chars,
                        '*',
                        self.smart_detect.get()
                    )

                    self.after(0, lambda: self.progress_bar.set(0.5))

                    # 加密原文
                    encrypted = encrypt_text(self.current_text, password, keywords)
                    encrypted_dict = asdict(encrypted)
                    encrypted_dict['created_at'] = datetime.now().isoformat(timespec="seconds")

                    self.after(0, lambda: self.progress_bar.set(0.8))

                    # 生成文件名（使用原始文件名+脱敏文件）
                    original_filename = os.path.splitext(os.path.basename(self.current_file))[0]
                    stamp = f"{original_filename}_脱敏文件"

                    # 使用增强格式生成文档（如果可用）
                    if self.current_paragraphs and self.use_enhanced_format:
                        # 对段落数据进行脱敏
                        masked_paragraphs = mask_paragraphs_data(self.current_paragraphs, masked, self.current_text)
                        masked_docx = build_docx_with_format(masked_paragraphs)
                    else:
                        # 使用普通方式生成文档
                        masked_docx = build_docx_bytes(masked)

                    bundle_bytes = build_zip_bundle(masked_docx, encrypted_dict, stamp)

                self.after(0, lambda: self.progress_bar.set(1.0))

                # 完成回调
                self.after(0, lambda: self.on_masking_complete(
                    masked, stats, bundle_bytes, stamp
                ))

            except Exception as e:
                self.after(0, lambda: self.on_masking_error(str(e)))

        threading.Thread(target=process_masking, daemon=True).start()

    def on_masking_complete(self, masked, stats, bundle_bytes, stamp):
        """脱敏完成回调"""
        self.processing = False
        self.bundle_bytes = bundle_bytes
        self.current_stamp = stamp

        self.mask_button.configure(state="normal", text="🚀 开始脱敏")
        self.mask_status.configure(
            text="✅ 脱敏完成！",
            text_color="#34d399"
        )

        # 更新结果展示
        self.result_preview.configure(state="normal")
        self.result_preview.delete("1.0", "end")
        preview_text = masked[:500] + "..." if len(masked) > 500 else masked
        self.result_preview.insert("1.0", preview_text)
        self.result_preview.configure(state="disabled")

        # 更新统计
        manual_count = stats.get("manual_keywords", 0)
        self.stat_labels["keywords"].configure(text=str(manual_count))

        smart_stats = stats.get("smart_detection", {})
        self.stat_labels["phone"].configure(text=str(smart_stats.get("手机号", 0)))
        self.stat_labels["idcard"].configure(text=str(smart_stats.get("身份证号", 0)))
        self.stat_labels["email"].configure(text=str(smart_stats.get("邮箱", 0)))
        self.stat_labels["credit_code"].configure(text=str(smart_stats.get("统一社会信用代码", 0)))
        self.stat_labels["company"].configure(text=str(smart_stats.get("企业名称", 0)))
        self.stat_labels["address"].configure(text=str(smart_stats.get("详细地址", 0)))
        self.stat_labels["bank_card"].configure(text=str(smart_stats.get("银行卡号", 0)))
        self.stat_labels["license_plate"].configure(text=str(smart_stats.get("车牌号", 0)))
        self.stat_labels["amount"].configure(text=str(smart_stats.get("金额", 0)))

        # 启用下载按钮
        self.download_button.configure(state="normal")

    def on_masking_error(self, error_msg):
        """脱敏错误回调"""
        self.processing = False
        self.mask_button.configure(state="normal", text="🚀 开始脱敏")
        self.progress_bar.set(0)
        self.mask_status.configure(
            text=f"❌ 处理失败",
            text_color="red"
        )
        CTkMessagebox.show_error(self, "处理失败", error_msg)

    def on_download_click(self):
        """处理下载按钮点击"""
        if not self.bundle_bytes:
            return

        file_path = filedialog.asksaveasfilename(
            title="保存脱敏包",
            defaultextension=".zip",
            initialfile=f"masked_bundle_{self.current_stamp}.zip",
            filetypes=[
                ("ZIP文件", "*.zip"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    f.write(self.bundle_bytes)
                CTkMessagebox.show_success(
                    self, "保存成功", "脱敏包已保存成功！"
                )
            except Exception as e:
                CTkMessagebox.show_error(self, "保存失败", str(e))

    def on_restore_file_click(self):
        """处理还原文件选择"""
        file_path = filedialog.askopenfilename(
            title="选择加密还原文件",
            filetypes=[
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.restore_file_path = file_path
            self.restore_file_label.configure(
                text=f"✅ {os.path.basename(file_path)}",
                text_color="#34d399"
            )

    def on_restore_click(self):
        """处理还原按钮点击"""
        if not hasattr(self, 'restore_file_path') or not self.restore_file_path:
            CTkMessagebox.show_error(self, "错误", "请选择加密还原文件")
            return

        password = self.restore_password_input.get()
        if not password:
            CTkMessagebox.show_error(self, "错误", "请输入还原密码")
            return

        # 显示处理中
        self.restore_button.configure(state="disabled", text="⏳ 解密中...")
        self.restore_status.configure(
            text="⏳ 解密中...",
            text_color="yellow"
        )

        # 在后台线程解密
        def process_restore():
            try:
                import json

                # 读取JSON文件
                with open(self.restore_file_path, 'r', encoding='utf-8') as f:
                    payload = json.load(f)

                # 解密
                plain = decrypt_text(payload, password)

                # 生成文档
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                restored_docx = build_docx_bytes(plain)

                # 完成回调
                def save_file():
                    file_path = filedialog.asksaveasfilename(
                        title="保存还原文档",
                        defaultextension=".docx",
                        initialfile=f"restored_{stamp}.docx",
                        filetypes=[
                            ("Word文档", "*.docx"),
                            ("所有文件", "*.*")
                        ]
                    )
                    if file_path:
                        try:
                            with open(file_path, 'wb') as f:
                                f.write(restored_docx)

                            self.restore_button.configure(state="normal", text="🔓 解密并下载原文")
                            self.restore_status.configure(
                                text="✅ 解密成功！",
                                text_color="#34d399"
                            )
                            CTkMessagebox.show_success(self, "保存成功", "文档保存成功！")
                        except Exception as e:
                            self.restore_button.configure(state="normal", text="🔓 解密并下载原文")
                            CTkMessagebox.show_error(self, "保存失败", str(e))
                    else:
                        self.restore_button.configure(state="normal", text="🔓 解密并下载原文")
                        self.restore_status.configure(text="已取消", text_color="gray")

                self.after(0, save_file)

            except ValueError as e:
                self.after(0, lambda: self.on_restore_error(str(e)))
            except Exception as e:
                self.after(0, lambda: self.on_restore_error(str(e)))

        threading.Thread(target=process_restore, daemon=True).start()

    def on_restore_error(self, error_msg):
        """还原错误回调"""
        self.restore_button.configure(state="normal", text="🔓 解密并下载原文")
        self.restore_status.configure(
            text=f"❌ 解密失败",
            text_color="red"
        )
        CTkMessagebox.show_error(self, "解密失败", "请检查密码或文件是否正确")


def main():
    """主函数"""
    app = MaskingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
