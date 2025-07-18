#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown中文格式转换器 - 用户友好版（优化布局）
支持直观的标题格式选择，无需了解正则表达式
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
import re
import json
import os
import platform

class MarkdownConverter:
    def __init__(self):
        self.chinese_numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        self.roman_numbers = ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ']
        self.reset_counters()
        
        # 预定义的标题格式库
        self.title_patterns = {
            # 输入格式的正则表达式，修改为严格匹配
            'markdown_h4': {'pattern': r'^####\s+(.+)$', 'name': '#### 标题'},  # 严格匹配4个#
            'markdown_h3': {'pattern': r'^###\s+(.+)$', 'name': '### 标题'},    # 严格匹配3个#
            'markdown_h2': {'pattern': r'^##\s+(.+)$', 'name': '## 标题'},      # 严格匹配2个#
            'markdown_h1': {'pattern': r'^#\s+(.+)$', 'name': '# 标题'},        # 严格匹配1个#
            'chinese_paren': {'pattern': r'^（([一二三四五六七八九十]+)）\s*(.+)$', 'name': '（一）标题'},
            'chinese_dot': {'pattern': r'^([一二三四五六七八九十]+)、\s*(.+)$', 'name': '一、标题'},
            'number_paren': {'pattern': r'^\((\d+)\)\s*(.+)$', 'name': '(1)标题'},
            'number_dot': {'pattern': r'^(\d+)、\s*(.+)$', 'name': '1、标题'},
            'number_period': {'pattern': r'^(\d+)\.\s+(.+)$', 'name': '1. 标题'},
            'letter_paren': {'pattern': r'^\(([A-Z])\)\s*(.+)$', 'name': '(A)标题'},
            'letter_period': {'pattern': r'^([A-Z])\.\s+(.+)$', 'name': 'A. 标题'},
            'letter_paren_lower': {'pattern': r'^\(([a-z])\)\s*(.+)$', 'name': '(a)标题'},
            'dash': {'pattern': r'^-\s+(.+)$', 'name': '- 标题'},
            'asterisk': {'pattern': r'^\*\s+(.+)$', 'name': '* 标题'},
            'roman_paren': {'pattern': r'^（([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+)）\s*(.+)$', 'name': '（Ⅰ）标题'},
            'roman_dot': {'pattern': r'^([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+)、\s*(.+)$', 'name': 'Ⅰ、标题'},
            'plain_text': {'pattern': r'^(.+)$', 'name': '普通文本（匹配所有）'}
        }
    
    def reset_counters(self):
        self.counters = {
            'level1': 0,
            'level2': 0,
            'level3': 0,
            'level4': 0
        }
    
    def clean_existing_title_numbers(self, title):
        """清理标题中已有的编号，包括各种常见编号格式"""
        patterns = [
            r'^[#*\s]*[一二三四五六七八九十]+[、.．]\s*',           # 中文数字+、/./．
            r'^[#*\s]*[0-9]+[、.．]\s*',                        # 数字+、/./．
            r'^[#*\s]*[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+[、.．]\s*',              # 罗马数字+、/./．
            r'^[#*\s]*[（(][一二三四五六七八九十0-9ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩa-zA-Z]+[)）]\s*', # 括号编号
            r'^[#*\s]*[A-Za-z][.．]\s*',                        # 字母+点
            r'^[#*\s]*[一二三四五六七八九十]+\s+',                # 中文数字+空格
            r'^[#*\s]*[0-9]+\s+',                               # 数字+空格
            r'^[#*\s]*[A-Za-z]+\s+',                            # 字母+空格
            r'^#+\s*',  # 清理开头的 # 符号
        ]
        for pattern in patterns:
            title = re.sub(pattern, '', title)
        return title.strip()
    
    def clean_markdown_symbols(self, text):
        """清除Markdown符号，保留文本内容"""
        # 清除标题符号 (# 开头)
        text = re.sub(r'^#+\s*', '', text)
        # 清除分隔线 (--- 或 ***)
        text = re.sub(r'^\s*[-*]{3,}\s*$', '', text)
        # 清除列表符号 (- * + 开头)
        text = re.sub(r'^[-*+]+\s+', '', text)
        # 清除数字列表 (1. 2. 等开头)
        text = re.sub(r'^\d+\.\s+', '', text)
        # 清除粗体和斜体标记 (** * __ _)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # 粗体 **text**
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # 斜体 *text*
        text = re.sub(r'__(.*?)__', r'\1', text)      # 粗体 __text__
        text = re.sub(r'_(.*?)_', r'\1', text)        # 斜体 _text_
        # 清除反引号代码块 (`code`)
        text = re.sub(r'`(.*?)`', r'\1', text)
        # 清除链接 [text](url)
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        # 清除图片 ![alt](url)
        text = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', text)
        # 清除引用符号 (> 开头)
        text = re.sub(r'^>\s+', '', text)
        # 清除三个井号标记 (### 开头)
        text = re.sub(r'^###\s+', '', text)
        # 清除两个星号标记 (**开头或结尾)
        text = re.sub(r'^\*\*', '', text)
        text = re.sub(r'\*\*$', '', text)
        # 清除行内的星号标记
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # 清除行末的星号标记
        text = re.sub(r'\*\*\s*$', '', text)
        text = re.sub(r'\*$', '', text)  # 清除单个星号结尾
        # 清除所有剩余的#和*
        text = re.sub(r'[#*]+', '', text)
        return text.strip()
    
    def get_chinese_number(self, num):
        if num <= 10:
            return self.chinese_numbers[num - 1]
        elif num <= 20:
            if num == 10:
                return '十'
            else:
                return '十' + self.chinese_numbers[num - 11]
        else:
            tens = num // 10
            ones = num % 10
            if ones == 0:
                return self.chinese_numbers[tens - 1] + '十'
            else:
                return self.chinese_numbers[tens - 1] + '十' + self.chinese_numbers[ones - 1]
    
    def get_roman_number(self, num):
        if num <= 10:
            return self.roman_numbers[num - 1]
        elif num <= 20:
            return f"Ⅹ{self.roman_numbers[num - 11]}"
        else:
            return "Ⅹ"
    
    def get_formatted_title(self, level, title, formats):
        prefix = ''
        
        if level == 1:
            self.counters['level1'] += 1
            self.counters['level2'] = 0
            self.counters['level3'] = 0
            self.counters['level4'] = 0
            
            if formats['level1'] == 'chinese':
                prefix = self.get_chinese_number(self.counters['level1']) + '、'
            elif formats['level1'] == 'number':
                prefix = str(self.counters['level1']) + '、'
            elif formats['level1'] == 'roman':
                prefix = self.get_roman_number(self.counters['level1']) + '、'
        
        elif level == 2:
            self.counters['level2'] += 1
            self.counters['level3'] = 0
            self.counters['level4'] = 0
            
            if formats['level2'] == 'chinese_paren':
                prefix = '（' + self.get_chinese_number(self.counters['level2']) + '）'
            elif formats['level2'] == 'number_paren':
                prefix = '(' + str(self.counters['level2']) + ')'
            elif formats['level2'] == 'letter_paren':
                prefix = '(' + chr(64 + self.counters['level2']) + ')'
        
        elif level == 3:
            self.counters['level3'] += 1
            self.counters['level4'] = 0
            
            if formats['level3'] == 'number_dot':
                prefix = str(self.counters['level3']) + '. '
            elif formats['level3'] == 'letter_dot':
                prefix = chr(64 + self.counters['level3']) + '. '
            elif formats['level3'] == 'chinese_dot':
                prefix = self.get_chinese_number(self.counters['level3']) + '. '
        
        elif level == 4:
            self.counters['level4'] += 1
            
            if formats['level4'] == 'number_paren':
                prefix = '(' + str(self.counters['level4']) + ')'
            elif formats['level4'] == 'letter_paren':
                prefix = '(' + chr(96 + self.counters['level4']) + ')'
            elif formats['level4'] == 'chinese_paren':
                prefix = '（' + self.get_chinese_number(self.counters['level4']) + '）'
        
        return prefix + title
    
    def convert_text(self, text, input_rules, output_formats):
        """转换整个文本"""
        lines = text.split('\n')
        converted_lines = []
        self.reset_counters()
        current_paragraph = []
        list_indent_level = 0
        in_list = False
        last_line_was_title = False
        
        # 创建一个按特定规则排序的规则列表
        # 1. 优先处理markdown标题，按#数量从多到少排序（即从低级别到高级别）
        # 2. 然后处理其他格式
        sorted_rules = []
        markdown_rules = []
        other_rules = []
        
        for level_name, pattern_key in input_rules.items():
            if pattern_key and pattern_key in self.title_patterns:
                if pattern_key.startswith('markdown_'):
                    # 提取#的数量，用于排序
                    hash_count = pattern_key.count('h')
                    markdown_rules.append((level_name, pattern_key, hash_count))
                else:
                    other_rules.append((level_name, pattern_key))
        
        # 对markdown标题规则按#数量从多到少排序（即从低级别到高级别）
        markdown_rules.sort(key=lambda x: -x[2])  # 负号表示降序
        
        # 合并排序后的规则
        for rule in markdown_rules:
            sorted_rules.append((rule[0], rule[1]))
        sorted_rules.extend(other_rules)
        
        for i, line in enumerate(lines):
            original_line = line.strip()
            # 跳过分隔线
            if re.match(r'^\s*[-*]{3,}\s*$', original_line):
                continue
            if not original_line:
                if current_paragraph:
                    converted_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                if in_list:
                    in_list = False
                    list_indent_level = 0
                continue
            
            matched = False
            # 使用排序后的规则列表
            for level_name, pattern_key in sorted_rules:
                if pattern_key in self.title_patterns:
                    pattern = self.title_patterns[pattern_key]['pattern']
                    match = re.match(pattern, original_line)
                    if match:
                        if current_paragraph:
                            converted_lines.append(' '.join(current_paragraph))
                            current_paragraph = []
                        in_list = False
                        list_indent_level = 0
                                                # 提取标题内容 - 处理不同的匹配组
                        if len(match.groups()) == 1:
                            title = match.group(1).strip()
                        elif len(match.groups()) == 2:
                            title = match.group(2).strip()
                        else:
                            title = match.group(-1).strip()
                        # 先去Markdown符号，再去编号
                        clean_title = self.clean_markdown_symbols(title)
                        clean_title = self.clean_existing_title_numbers(clean_title)
                        level_num = int(level_name.replace('level', ''))
                        converted_title = self.get_formatted_title(level_num, clean_title, output_formats)
                        converted_lines.append(converted_title)
                        last_line_was_title = True
                        matched = True
                        break
            
            if not matched:
                cleaned_line = self.clean_markdown_symbols(original_line)
                list_match = re.match(r'^([-*+]|\d+\.|[a-zA-Z]\.)\s+', original_line)
                if list_match:
                    if current_paragraph:
                        converted_lines.append(' '.join(current_paragraph))
                        current_paragraph = []
                    in_list = True
                    last_line_was_title = False
                    converted_lines.append(cleaned_line)
                elif in_list and original_line.startswith('  '):
                    if converted_lines:
                        converted_lines[-1] = converted_lines[-1] + ' ' + cleaned_line
                    last_line_was_title = False
                else:
                    if not in_list:
                        current_paragraph.append(cleaned_line)
                    else:
                        in_list = False
                        current_paragraph.append(cleaned_line)
                    last_line_was_title = False
        
        if current_paragraph:
            converted_lines.append(' '.join(current_paragraph))
        
        result_lines = [line for line in converted_lines if line.strip()]
        return '\n'.join(result_lines)
        
    def _is_title_line(self, line):
        """判断一行是否是标题行（以数字、中文数字或罗马数字开头）"""
        return bool(re.match(r'^[一二三四五六七八九十]、|^\d+、|^[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]、|^（[一二三四五六七八九十]）|^\(\d+\)|^\([A-Za-z]\)', line))

class MarkdownConverterGUI:
    def __init__(self, root):
        self.root = root
        self.converter = MarkdownConverter()
        self.last_input_rules = {}
        self.last_output_formats = {}
        self.rules_initialized = False  # 标记规则是否已初始化
        
        # 配置文件路径
        self.config_dir = os.path.join(os.path.expanduser("~"), ".markdown_converter")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # 确保配置目录存在
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # 设置跨平台字体
        self.setup_fonts()
        
        # 设置UI
        self.setup_ui()
        
        # 加载配置（如果存在）
        self.load_config()
        
        # 保存加载后的规则状态作为初始状态
        self.save_current_rules_state()
    
    def setup_fonts(self):
        """设置跨平台字体"""
        system = platform.system()
        
        # 默认字体
        self.default_font = "TkDefaultFont"
        self.title_font = "TkDefaultFont"
        self.text_font = "TkFixedFont"
        self.button_font = "TkDefaultFont"
        
        # 根据系统设置字体
        if system == "Windows":
            # Windows系统优先使用微软雅黑
            self.default_font = "Microsoft YaHei UI"
            self.title_font = "Microsoft YaHei UI"
            self.text_font = "Microsoft YaHei UI"
            self.button_font = "Microsoft YaHei UI"
        elif system == "Darwin":  # macOS
            # macOS系统使用系统默认字体
            self.default_font = "PingFang SC"
            self.title_font = "PingFang SC"
            self.text_font = "PingFang SC"
            self.button_font = "PingFang SC"
        elif system == "Linux":
            # Linux系统尝试使用文泉驿或Noto Sans
            self.default_font = "Noto Sans CJK SC"
            self.title_font = "Noto Sans CJK SC"
            self.text_font = "Noto Sans Mono CJK SC"
            self.button_font = "Noto Sans CJK SC"
        
        # 检查字体是否可用
        try:
            available_fonts = list(font.families())
            
            if self.default_font not in available_fonts:
                self.default_font = "TkDefaultFont"
            if self.text_font not in available_fonts:
                self.text_font = "TkFixedFont"
        except Exception:
            # 如果获取字体列表失败，使用默认字体
            self.default_font = "TkDefaultFont"
            self.title_font = "TkDefaultFont"
            self.text_font = "TkFixedFont"
            self.button_font = "TkDefaultFont"
        
    def setup_ui(self):
        self.root.title("Markdown中文格式转换器")
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算窗口尺寸 - 宽度为屏幕宽度的80%，高度为屏幕高度的80%
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # 确保窗口不会太小
        window_width = max(window_width, 1000)
        window_height = max(window_height, 700)
        
        # 计算窗口位置使其居中
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.configure(bg='#f0f0f0')
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 主内容框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 创建Notebook（标签页）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # 第一个标签页：转换器
        converter_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(converter_frame, text="📄 文本转换")
        
        # 第二个标签页：格式规则
        rules_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(rules_frame, text="⚙️ 格式规则")
        
        # 设置转换器页面
        self.setup_converter_page(converter_frame)
        
        # 设置格式规则页面
        self.setup_rules_page(rules_frame)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w',
            bg='#ecf0f1',
            fg='#2c3e50',
            font=(self.default_font, 9)
        )
        status_bar.pack(side='bottom', fill='x')
        
        # 绑定快捷键
        self.root.bind('<Control-Return>', lambda e: self.convert_text())
        self.root.bind('<F5>', lambda e: self.convert_text())
        
        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # 绑定窗口关闭事件，保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_converter_page(self, parent):
        """设置转换器页面"""
        # 左右分栏
        content_frame = tk.Frame(parent, bg='#f0f0f0')
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧输入区域
        left_frame = tk.LabelFrame(
            content_frame, 
            text="📄 输入区域", 
            font=(self.default_font, 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=10,
            pady=5  # 减小内边距
        )
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 输入区域按钮框架 - 移到文本框前面
        input_button_frame = tk.Frame(left_frame, bg='white')
        input_button_frame.pack(fill='x', pady=(0, 5))  # 减小内边距
        
        # 清空按钮
        self.clear_btn = tk.Button(
            input_button_frame,
            text="🗑️ 清空内容",
            command=self.clear_all,
            bg='#95a5a6',
            fg='black',
            font=(self.button_font, 9, 'bold'),  # 减小字体
            relief='flat',
            padx=10,
            pady=3,  # 减小内边距
            cursor='hand2'
        )
        self.clear_btn.pack(side='left', padx=(0, 10))
        
        # 刷新按钮
        self.refresh_btn = tk.Button(
            input_button_frame,
            text="🔄 刷新",
            command=self.auto_convert,
            bg='#3498db',
            fg='black',
            font=(self.button_font, 9, 'bold'),  # 减小字体
            relief='flat',
            padx=10,
            pady=3,  # 减小内边距
            cursor='hand2'
        )
        self.refresh_btn.pack(side='left')
        
        # 输入文本框
        self.input_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            font=(self.text_font, 10),  # 减小字体
            bg='#fafafa',
            fg='#333333',
            insertbackground='#2c3e50',
            selectbackground='#3498db',
            selectforeground='white'
        )
        self.input_text.pack(fill='both', expand=True)
        
        # 绑定输入文本变化事件，实现自动转换
        self.input_text.bind("<KeyRelease>", self.auto_convert)
        
        # 添加示例文本
        example_text = """"""
        
        self.input_text.insert('1.0', example_text)
        
        # 初始加载时自动执行一次转换
        self.root.after(100, self.auto_convert)
        
        # 右侧输出区域
        right_frame = tk.LabelFrame(
            content_frame, 
            text="✨ 转换结果", 
            font=(self.default_font, 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=10,
            pady=5  # 减小内边距
        )
        right_frame.pack(side='right', fill='both', expand=True)
        
        # 输出区域复制按钮框架
        copy_frame = tk.Frame(right_frame, bg='white')
        copy_frame.pack(fill='x', pady=(0, 5))  # 减小内边距
        
        self.copy_selected_btn = tk.Button(
            copy_frame,
            text="📋 复制选中",
            command=self.copy_selected,
            bg='#3498db',
            fg='black',
            font=(self.button_font, 9, 'bold'),  # 减小字体
            relief='flat',
            padx=10,
            pady=3,  # 减小内边距
            cursor='hand2'
        )
        self.copy_selected_btn.pack(side='left', padx=(0, 10))
        
        self.copy_all_btn = tk.Button(
            copy_frame,
            text="📄 复制全部",
            command=self.copy_all,
            bg='#27ae60',
            fg='black',
            font=(self.button_font, 9, 'bold'),  # 减小字体
            relief='flat',
            padx=10,
            pady=3,  # 减小内边距
            cursor='hand2'
        )
        self.copy_all_btn.pack(side='left')
        
        # 输出文本框
        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=(self.text_font, 10),  # 减小字体
            bg='#f8f9fa',
            fg='#333333',
            insertbackground='#2c3e50',
            selectbackground='#3498db',
            selectforeground='white',
            state='normal'
        )
        self.output_text.pack(fill='both', expand=True)
        
        # 设置按钮悬停效果
        self.setup_hover_effects()
    
    def setup_rules_page(self, parent):
        """设置格式规则页面"""
        # 创建左右分栏
        main_content = tk.Frame(parent, bg='#f0f0f0')
        main_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧设置区域
        left_frame = tk.Frame(main_content, bg='#f0f0f0')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 右侧预览区域
        right_frame = tk.Frame(main_content, bg='#f0f0f0')
        right_frame.pack(side='right', fill='both', expand=True)
        
        # 设置左侧内容
        self.setup_left_rules_content(left_frame)
        
        # 设置右侧内容
        self.setup_right_preview_content(right_frame)
    
    def setup_left_rules_content(self, parent):
        """设置左侧规则配置内容""" 
        # 输入格式设置
        input_frame = tk.LabelFrame(
            parent,
            text="📥 输入格式设置（当前文本的标题是什么样子的）",
            font=(self.default_font, 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        input_frame.pack(fill='x', pady=(0, 10))
        
        # 输出格式设置
        output_frame = tk.LabelFrame(
            parent,
            text="📤 输出格式设置（希望转换后的标题是什么样子的）",
            font=(self.default_font, 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        output_frame.pack(fill='x', pady=(0, 10))
        
        # 快速预设按钮 - 修改布局
        preset_frame = tk.LabelFrame(
            parent,
            text="🚀 快速预设",
            font=(self.default_font, 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        preset_frame.pack(fill='both', expand=True, pady=(0, 10))  # 使用 expand=True
        
        # 创建输入和输出格式选择器
        self.setup_input_format_selectors(input_frame)
        self.setup_output_format_selectors(output_frame)
        self.setup_preset_buttons(preset_frame)
    
    def setup_right_preview_content(self, parent):
        """设置右侧预览内容 - 改为左右对比"""
        
        # 实时预览区域 - 填满整个右侧区域
        preview_frame = tk.LabelFrame(
            parent,
            text="👁️ 实时预览对比",
            font=('微软雅黑', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        preview_frame.pack(fill='both', expand=True, pady=0)
        
        # 预览说明
        preview_info = tk.Label(
            preview_frame,
            text="根据你的设置，以下是转换效果对比预览：",
            font=('微软雅黑', 10),
            bg='white',
            fg='#2c3e50'
        )
        preview_info.pack(anchor='w', pady=(0, 5))
        
        # 创建左右对比容器
        preview_container = tk.Frame(preview_frame, bg='white')
        preview_container.pack(fill='both', expand=True, pady=0)
        
        # 添加这两行来配置等分
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_columnconfigure(1, weight=1)
        preview_container.grid_rowconfigure(0, weight=1)

        # 左侧：转换前
        before_frame = tk.LabelFrame(
            preview_container,
            text="📄 转换前",
            font=('微软雅黑', 11, 'bold'),
            bg='white',
            fg='#e74c3c',
            padx=10,
            pady=10
        )
        before_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 2))
        
        self.preview_before_text = scrolledtext.ScrolledText(
            before_frame,
            wrap=tk.WORD,
            font=('微软雅黑', 10),
            bg='#fff3f3',
            fg='#333333',
            state='normal'
        )
        self.preview_before_text.pack(fill='both', expand=True)
        
        # 右侧：转换后
        after_frame = tk.LabelFrame(
            preview_container,
            text="✨ 转换后",
            font=('微软雅黑', 11, 'bold'),
            bg='white',
            fg='#27ae60',
            padx=10,
            pady=10
        )
        after_frame.grid(row=0, column=1, sticky='nsew', padx=(2, 0))
        
        self.preview_after_text = scrolledtext.ScrolledText(
            after_frame,
            wrap=tk.WORD,
            font=('微软雅黑', 10),
            bg='#f3fff3',
            fg='#333333',
            state='normal'
        )
        self.preview_after_text.pack(fill='both', expand=True)
        
        # 初始化预览
        self.update_preview()
    
    def update_preview(self):
        """更新预览内容 - 左右对比版本"""
        try:
            # 获取当前设置
            input_rules = self.get_input_rules()
            output_formats = self.get_output_formats()
            
            # 示例文本
            sample_text = """以下是常用标题格式的示例文档，可以测试不同格式的转换效果：

# 一级标题示例（# 开头）
## 二级标题示例（## 开头）
### 三级标题示例（### 开头）
#### 四级标题示例（#### 开头）

（一）中文数字括号标题示例
（二）第二个中文括号标题
（三）第三个中文括号标题

一、中文数字顿号标题示例
二、第二个中文顿号标题
三、第三个中文顿号标题

(1) 阿拉伯数字括号标题示例
(2) 第二个数字括号标题
(3) 第三个数字括号标题

1、阿拉伯数字顿号标题示例
2、第二个数字顿号标题
3、第三个数字顿号标题
1. 阿拉伯数字点号标题示例
2. 第二个数字点号标题
3. 第三个数字点号标题

- 短横线列表标题示例
- 第二个短横线标题
* 星号列表标题示例
* 第二个星号标题

### 1. **混合格式标题示例（Markdown + 数字 + 粗体）**
### 2. **《关于促进大功率充电设施科学规划建设的通知》（发改办能源〔2025〕632号）**

**发布机构**：国家发展改革委办公厅、国家能源局综合司
**主要内容**：提出到2027年底，力争全国大功率充电设施超过10万台

这是普通文本段落，不会被识别为标题格式。
以上示例涵盖了所有支持的标题格式，你可以通过设置不同的输入输出规则来测试转换效果。"""
            
            # 更新转换前的内容
            self.preview_before_text.delete('1.0', tk.END)
            self.preview_before_text.insert('1.0', sample_text)
            
            # 更新转换后的内容
            if input_rules:
               
                # 先找出所有会被转换的原始标题内容
                original_lines = sample_text.split('\n')
                converted_titles = set()  # 存储会被转换的标题的清理后内容
                
                for original_line in original_lines:
                    if not original_line.strip():
                        continue
                        
                    for level_name, pattern_key in input_rules.items():
                        if pattern_key and pattern_key in self.converter.title_patterns:
                            pattern = self.converter.title_patterns[pattern_key]['pattern']
                            match = re.match(pattern, original_line)
                            if match:
                                # 提取并清理标题内容
                                if len(match.groups()) == 1:
                                    title = match.group(1).strip()
                                elif len(match.groups()) == 2:
                                    title = match.group(2).strip()
                                else:
                                    title = match.group(-1).strip()
                                
                                clean_title = self.converter.clean_markdown_symbols(title)
                                clean_title = self.converter.clean_existing_title_numbers(clean_title)
                                converted_titles.add(clean_title)
                                break
                
                # 进行转换
                result = self.converter.convert_text(sample_text, input_rules, output_formats)
                
                # 清空转换后的文本框
                self.preview_after_text.delete('1.0', tk.END)
                
                # 配置文本标签样式
                self.preview_after_text.tag_configure("modified", background="#ffffcc", foreground="#d35400", font=('微软雅黑', 10, 'bold'))
                self.preview_after_text.tag_configure("normal", background="#f3fff3", foreground="#333333")
                
                # 先插入所有文本
                self.preview_after_text.insert('1.0', result)
                
                # 检查转换后的每一行
                result_lines = result.split('\n')
                for i, line in enumerate(result_lines):
                    line_start = f"{i+1}.0"
                    line_end = f"{i+1}.end"
                    
                    is_modified = False
                    if line.strip():
                        # 检查这行是否包含被转换的标题内容
                        for converted_title in converted_titles:
                            if converted_title and converted_title in line:
                                is_modified = True
                                break
                    
                    # 应用样式标签
                    if is_modified:
                        self.preview_after_text.tag_add("modified", line_start, line_end)
                    else:
                        self.preview_after_text.tag_add("normal", line_start, line_end)
            else:
                self.preview_after_text.delete('1.0', tk.END)
                self.preview_after_text.insert('1.0', "请先设置输入格式，然后点击【更新预览】查看转换效果")
        except Exception as e:
            error_msg = f"预览更新失败：{str(e)}"
            self.preview_after_text.delete('1.0', tk.END)
            self.preview_after_text.insert('1.0', error_msg)
    
    def setup_input_format_selectors(self, parent):
        """设置输入格式选择器"""
        self.input_vars = {}
        
        # 可用的输入格式选项
        input_options = [
            ('不使用', ''),
            ('#### 标题', 'markdown_h4'),
            ('### 标题', 'markdown_h3'),
            ('## 标题', 'markdown_h2'),
            ('# 标题', 'markdown_h1'),
            ('（一）标题', 'chinese_paren'),
            ('一、标题', 'chinese_dot'),
            ('(1)标题', 'number_paren'),
            ('1、标题', 'number_dot'),
            ('1. 标题', 'number_period'),
            ('(A)标题', 'letter_paren'),
            ('A. 标题', 'letter_period'),
            ('(a)标题', 'letter_paren_lower'),
            ('- 标题', 'dash'),
            ('* 标题', 'asterisk'),
            ('（Ⅰ）标题', 'roman_paren'),
            ('Ⅰ、标题', 'roman_dot'),
        ]
        
        # 创建输入格式映射
        self.input_option_mapping = {opt[0]: opt[1] for opt in input_options}
        self.display_to_internal = {opt[0]: opt[1] for opt in input_options}
        self.internal_to_display = {opt[1]: opt[0] for opt in input_options if opt[1]}
        
        levels = [
            ('level1', '一级标题'),
            ('level2', '二级标题'),
            ('level3', '三级标题'),
            ('level4', '四级标题')
        ]
        
        for i, (level, level_name) in enumerate(levels):
            # 创建框架
            level_frame = tk.Frame(parent, bg='white')
            level_frame.pack(fill='x', pady=5)
            
            # 标签
            tk.Label(
                level_frame,
                text=f"{level_name}:",
                font=(self.default_font, 10, 'bold'),
                bg='white',
                fg='#2c3e50',
                width=10
            ).pack(side='left', padx=(0, 10))
            
            # 下拉框
            self.input_vars[level] = tk.StringVar()
            
            combobox = ttk.Combobox(
                level_frame,
                textvariable=self.input_vars[level],
                values=[opt[0] for opt in input_options],
                state='readonly',
                width=20,
                font=(self.default_font, 10)
            )
            combobox.pack(side='left', padx=(0, 10))
            
            # 绑定变化事件到预览更新和规则状态保存
            def on_change(event, self=self):
                if hasattr(self, 'update_preview'):
                    self.update_preview()
                    # 保存当前规则状态
                    self.save_current_rules_state()
            
            combobox.bind('<<ComboboxSelected>>', on_change)
            
            # 设置默认值
            defaults = ['（一）标题', '- 标题', '* 标题', '1. 标题']
            if i < len(defaults):
                self.input_vars[level].set(defaults[i])
            else:
                self.input_vars[level].set('不使用')
            
            # 预览按钮
            preview_btn = tk.Button(
                level_frame,
                text="👁 预览",
                command=lambda l=level: self.preview_input_format(l),
                bg='#f39c12',
                fg='black',
                font=(self.button_font, 9),
                padx=10,
                pady=2
            )
            preview_btn.pack(side='left', padx=5)
        
        # 不再需要在这里保存初始状态，因为我们在__init__中已经处理了
    
    def setup_output_format_selectors(self, parent):
        """设置输出格式选择器"""
        # 格式设置
        format_options = {
            'level1': {
                'label': '一级标题输出',
                'options': [
                    ('一、二、三、', 'chinese'),
                    ('1、2、3、', 'number'),
                    ('Ⅰ、Ⅱ、Ⅲ、', 'roman')
                ],
                'default': 'chinese'
            },
            'level2': {
                'label': '二级标题输出',
                'options': [
                    ('（一）（二）（三）', 'chinese_paren'),
                    ('(1)(2)(3)', 'number_paren'),
                    ('(A)(B)(C)', 'letter_paren')
                ],
                'default': 'chinese_paren'
            },
            'level3': {
                'label': '三级标题输出',
                'options': [
                    ('1. 2. 3.', 'number_dot'),
                    ('A. B. C.', 'letter_dot'),
                    ('一. 二. 三.', 'chinese_dot')
                ],
                'default': 'number_dot'
            },
            'level4': {
                'label': '四级标题输出',
                'options': [
                    ('(1)(2)(3)', 'number_paren'),
                    ('(a)(b)(c)', 'letter_paren'),
                    ('（一）（二）（三）', 'chinese_paren')
                ],
                'default': 'number_paren'
            }
        }
        
        # 初始化变量和映射
        self.output_vars = {}
        self.output_mappings = {}
        
        for i, (level, config) in enumerate(format_options.items()):
            # 创建框架
            level_frame = tk.Frame(parent, bg='white')
            level_frame.pack(fill='x', pady=5)
            
            # 标签
            tk.Label(
                level_frame,
                text=config['label'] + ":",
                font=(self.default_font, 10, 'bold'),
                bg='white',
                fg='#2c3e50',
                width=12
            ).pack(side='left', padx=(0, 10))
            
            # 创建显示值列表和映射关系
            display_values = [opt[0] for opt in config['options']]
            value_mapping = {opt[0]: opt[1] for opt in config['options']}
            reverse_mapping = {opt[1]: opt[0] for opt in config['options']}
            
            # 存储映射关系
            self.output_mappings[level] = value_mapping
            
            # 下拉框
            self.output_vars[level] = tk.StringVar()
            
            combobox = ttk.Combobox(
                level_frame,
                textvariable=self.output_vars[level],
                values=display_values,
                state='readonly',
                width=20,
                font=(self.default_font, 10)
            )
            combobox.pack(side='left', padx=(0, 10))
            
            # 绑定变化事件到预览更新和规则状态保存
            def on_change(event, self=self):
                if hasattr(self, 'update_preview'):
                    self.update_preview()
                    # 保存当前规则状态
                    self.save_current_rules_state()
            
            combobox.bind('<<ComboboxSelected>>', on_change)
            
            # 设置默认显示值
            default_display = reverse_mapping.get(config['default'], display_values[0])
            self.output_vars[level].set(default_display)
            
            # 示例按钮
            example_btn = tk.Button(
                level_frame,
                text="📝 示例",
                command=lambda l=level: self.show_output_example(l),
                bg='#9b59b6',
                fg='black',
                font=(self.button_font, 9),
                padx=10,
                pady=2
            )
            example_btn.pack(side='left', padx=5)
    
    def setup_preset_buttons(self, parent):
        """设置预设按钮 - 优化布局"""
        presets = [
            {
                'name': '标准文档格式',
                'description': '一、（一）1. (1)',
                'input': {
                    'level1': '（一）标题',
                    'level2': '1、标题',
                    'level3': '- 标题',
                    'level4': '* 标题'
                },
                'output': {
                    'level1': '一、标题',
                    'level2': '（一）标题',
                    'level3': '1. 标题',
                    'level4': '(1)标题'
                }
            },
            {
                'name': 'Markdown转中文',
                'description': '#### → 一、',
                'input': {
                    'level1': '#### 标题',
                    'level2': '### 标题',
                    'level3': '## 标题',
                    'level4': '# 标题'
                },
                'output': {
                    'level1': '一、标题',
                    'level2': '（一）标题',
                    'level3': '1. 标题',
                    'level4': '(1)标题'
                }
            },
            {
                'name': '全数字格式',
                'description': '1、(1)1. (a)',
                'input': {
                    'level1': '（一）标题',
                    'level2': '- 标题',
                    'level3': '* 标题',
                    'level4': '1. 标题'
                },
                'output': {
                    'level1': '1、标题',
                    'level2': '(1)标题',
                    'level3': '1. 标题',
                    'level4': '(a)标题'
                }
            }
        ]
        
        # 创建网格布局来更好地显示预设按钮
        for i, preset in enumerate(presets):
            preset_container = tk.Frame(parent, bg='white', relief='raised', bd=1)
            preset_container.pack(fill='x', pady=5, padx=5)  # 减小垂直内边距
            
            # 预设按钮
            btn = tk.Button(
                preset_container,
                text=f"{preset['name']}",
                command=lambda p=preset: self.apply_preset(p),
                bg='#3498db',
                fg='black',
                font=(self.button_font, 10, 'bold'),
                padx=15,
                pady=6,
                width=6  # 进一步减小按钮宽度
            )
            btn.pack(side='left', padx=10, pady=1)
            
            # 描述区域
            desc_frame = tk.Frame(preset_container, bg='white')
            desc_frame.pack(side='left', fill='both', expand=True, padx=5)
            
            # 输入格式描述 - 增加字间距
            input_text = f"1: {preset['input']['level1']} | 2: {preset['input']['level2']} | 3: {preset['input']['level3']} | 4: {preset['input']['level4']}"
            input_label = tk.Label(
                desc_frame,
                text=f"输入: {input_text}",
                font=(self.default_font, 9),  # 减小字体大小
                bg='white',
                fg='#e74c3c',
                anchor='w',
                justify='left'  # 确保左对齐
            )
            input_label.pack(anchor='w', pady=(2, 1))  # 添加垂直间距
            
            # 输出格式描述 - 增加字间距
            output_text = f"1: {preset['output']['level1']} | 2: {preset['output']['level2']} | 3: {preset['output']['level3']} | 4: {preset['output']['level4']}"
            output_label = tk.Label(
                desc_frame,
                text=f"输出: {output_text}",
                font=(self.default_font, 9),  # 减小字体大小
                bg='white',
                fg='#27ae60',
                anchor='w',
                justify='left'  # 确保左对齐
            )
            output_label.pack(anchor='w', pady=(1, 2))  # 添加垂直间距
    
    def preview_input_format(self, level):
        """预览输入格式"""
        display_value = self.input_vars[level].get()
        if display_value == '不使用':
            messagebox.showinfo("预览", f"{level}: 此级别不使用")
            return
        
        pattern_key = self.input_option_mapping.get(display_value)
        
        if pattern_key and pattern_key in self.converter.title_patterns:
            pattern_info = self.converter.title_patterns[pattern_key]
            example_text = f"格式名称：{pattern_info['name']}\n\n"
            
            # 提供示例
            examples = {
                'markdown_h4': ['#### 这是标题', '#### 另一个标题'],
                'markdown_h3': ['### 这是标题', '### 另一个标题'],
                'markdown_h2': ['## 这是标题', '## 另一个标题'],
                'markdown_h1': ['# 这是标题', '# 另一个标题'],
                'chinese_paren': ['（一）这是标题', '（二）另一个标题'],
                'chinese_dot': ['一、这是标题', '二、另一个标题'],
                'number_paren': ['(1)这是标题', '(2)另一个标题'],
                'number_dot': ['1、这是标题', '2、另一个标题'],
                'number_period': ['1. 这是标题', '2. 另一个标题'],
                'letter_paren': ['(A)这是标题', '(B)另一个标题'],
                'letter_period': ['A. 这是标题', 'B. 另一个标题'],
                'letter_paren_lower': ['(a)这是标题', '(b)另一个标题'],
                'dash': ['- 这是标题', '- 另一个标题'],
                'asterisk': ['* 这是标题', '* 另一个标题'],
                'roman_paren': ['（Ⅰ）这是标题', '（Ⅱ）另一个标题'],
                'roman_dot': ['Ⅰ、这是标题', 'Ⅱ、另一个标题'],
            }
            
            if pattern_key in examples:
                example_text += "匹配示例：\n"
                for ex in examples[pattern_key]:
                    example_text += f"  ✓ {ex}\n"
            
            messagebox.showinfo("输入格式预览", example_text)
        else:
            # 显示右上角自动消失提示
            self.show_top_right_notification("未找到对应的格式信息")
    
    def show_output_example(self, level):
        """显示输出格式示例"""
        display_value = self.output_vars[level].get()
        
        examples = {
            'level1': {
                '一、二、三、': ['一、政策参与及实施成效', '二、国家级项目参与', '三、省级服务实践'],
                '1、2、3、': ['1、政策参与及实施成效', '2、国家级项目参与', '3、省级服务实践'],
                'Ⅰ、Ⅱ、Ⅲ、': ['Ⅰ、政策参与及实施成效', 'Ⅱ、国家级项目参与', 'Ⅲ、省级服务实践']
            },
            'level2': {
                '（一）（二）（三）': ['（一）专项行动参与', '（二）安全体系建设', '（三）企业服务覆盖'],
                '(1)(2)(3)': ['(1)专项行动参与', '(2)安全体系建设', '(3)企业服务覆盖'],
                '(A)(B)(C)': ['(A)专项行动参与', '(B)安全体系建设', '(C)企业服务覆盖']
            },
            'level3': {
                '1. 2. 3.': ['1. 工业诊所项目', '2. 企业上云工程', '3. 政策宣贯活动'],
                'A. B. C.': ['A. 工业诊所项目', 'B. 企业上云工程', 'C. 政策宣贯活动'],
                '一. 二. 三.': ['一. 工业诊所项目', '二. 企业上云工程', '三. 政策宣贯活动']
            },
            'level4': {
                '(1)(2)(3)': ['(1)组建专家团队', '(2)完成企业诊断', '(3)推动云端部署'],
                '(a)(b)(c)': ['(a)组建专家团队', '(b)完成企业诊断', '(c)推动云端部署'],
                '（一）（二）（三）': ['（一）组建专家团队', '（二）完成企业诊断', '（三）推动云端部署']
            }
        }
        
        if level in examples and display_value in examples[level]:
            example_list = examples[level][display_value]
            example_text = f"输出格式示例：\n\n"
            for ex in example_list:
                example_text += f"  {ex}\n"
            
            messagebox.showinfo("输出格式示例", example_text)
        else:
            # 显示右上角自动消失提示
            self.show_top_right_notification("未找到示例")
    
    def apply_preset(self, preset):
        """应用预设配置"""
        # 设置输入格式
        for level, format_name in preset['input'].items():
            if level in self.input_vars:
                self.input_vars[level].set(format_name)
        
        # 设置输出格式
        output_mappings = {
            'level1': {
                '一、标题': '一、二、三、',
                '1、标题': '1、2、3、',
                'Ⅰ、标题': 'Ⅰ、Ⅱ、Ⅲ、'
            },
            'level2': {
                '（一）标题': '（一）（二）（三）',
                '(1)标题': '(1)(2)(3)',
                '(A)标题': '(A)(B)(C)'
            },
            'level3': {
                '1. 标题': '1. 2. 3.',
                'A. 标题': 'A. B. C.',
                '一. 标题': '一. 二. 三.'
            },
            'level4': {
                '(1)标题': '(1)(2)(3)',
                '(a)标题': '(a)(b)(c)',
                '（一）标题': '（一）（二）（三）'
            }
        }
        
        for level, format_name in preset['output'].items():
            if level in self.output_vars and level in output_mappings:
                if format_name in output_mappings[level]:
                    self.output_vars[level].set(output_mappings[level][format_name])
        
        # 更新预览
        if hasattr(self, 'update_preview'):
            self.update_preview()
        
        # 保存当前配置到文件
        self.save_config_without_message()
        
        self.status_var.set(f"已应用预设：{preset['name']}")
        messagebox.showinfo("成功", f"已应用预设配置：{preset['name']}")
    

    
    def setup_hover_effects(self):
        """设置按钮悬停效果"""
        def on_enter(widget, color):
            def handler(e):
                widget.config(bg=color)
            return handler
        
        def on_leave(widget, color):
            def handler(e):
                widget.config(bg=color)
            return handler
        
        # 清空按钮
        self.clear_btn.bind("<Enter>", on_enter(self.clear_btn, '#7f8c8d'))
        self.clear_btn.bind("<Leave>", on_leave(self.clear_btn, '#95a5a6'))
        
        # 刷新按钮
        self.refresh_btn.bind("<Enter>", on_enter(self.refresh_btn, '#2980b9'))
        self.refresh_btn.bind("<Leave>", on_leave(self.refresh_btn, '#3498db'))
        
        # 复制按钮
        self.copy_selected_btn.bind("<Enter>", on_enter(self.copy_selected_btn, '#2980b9'))
        self.copy_selected_btn.bind("<Leave>", on_leave(self.copy_selected_btn, '#3498db'))
        
        self.copy_all_btn.bind("<Enter>", on_enter(self.copy_all_btn, '#229954'))
        self.copy_all_btn.bind("<Leave>", on_leave(self.copy_all_btn, '#27ae60'))
    
    def get_input_rules(self):
        """获取输入规则设置"""
        rules = {}
        for level, var in self.input_vars.items():
            display_value = var.get()
            if display_value != '不使用':
                internal_value = self.input_option_mapping.get(display_value)
                if internal_value:
                    rules[level] = internal_value
        return rules
    
    def get_output_formats(self):
        """获取输出格式设置"""
        formats = {}
        for key, var in self.output_vars.items():
            display_value = var.get()
            if hasattr(self, 'output_mappings') and key in self.output_mappings:
                internal_value = self.output_mappings[key].get(display_value, 'chinese')
                formats[key] = internal_value
            else:
                default_mapping = {
                    'level1': 'chinese',
                    'level2': 'chinese_paren', 
                    'level3': 'number_dot',
                    'level4': 'number_paren'
                }
                formats[key] = default_mapping.get(key, 'chinese')
        return formats
    
    def convert_text(self):
        """执行文本转换"""
        input_text = self.input_text.get('1.0', tk.END).strip()
        
        if not input_text:
            # 显示右上角自动消失提示
            self.show_top_right_notification("请先输入要转换的文本！")
            self.status_var.set("转换失败：输入为空")
            return
        
        try:
            input_rules = self.get_input_rules()
            output_formats = self.get_output_formats()
            
            if not input_rules:
                warning_msg = "请先在【格式规则】页面设置至少一个输入格式！"
                # 显示右上角自动消失提示
                self.show_top_right_notification(warning_msg)
                self.status_var.set("转换失败：未设置输入格式")
                return
            
            result = self.converter.convert_text(input_text, input_rules, output_formats)
            
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert('1.0', result)
            
            self.status_var.set("转换完成！")
            messagebox.showinfo("成功", "文本转换完成！")
            
        except Exception as e:
            error_msg = f"转换过程中出现错误：{str(e)}"
            messagebox.showerror("错误", error_msg)
            self.status_var.set(f"转换失败：{str(e)}")
    
    def auto_convert(self, event=None):
        """自动转换文本，无需点击按钮"""
        # 获取输入文本并去掉首尾空白
        input_text = self.input_text.get('1.0', tk.END).strip()
        
        if not input_text:
            self.output_text.delete('1.0', tk.END)
            return
        
        try:
            input_rules = self.get_input_rules()
            output_formats = self.get_output_formats()
            
            if not input_rules:
                self.output_text.delete('1.0', tk.END)
                self.output_text.insert('1.0', "请先在【格式规则】页面设置至少一个输入格式！")
                return

            # 执行转换（convert_text方法已经包含去除多余换行的逻辑）
            result = self.converter.convert_text(input_text, input_rules, output_formats)
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert('1.0', result)
            
            if hasattr(self, 'status_var') and self.status_var.get().startswith("格式规则已更改"):
                self.status_var.set("格式规则已更改，转换结果已更新")
            else:
                self.status_var.set("自动转换完成")
            
        except Exception as e:
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert('1.0', f"转换过程中出现错误：{str(e)}")
            self.status_var.set(f"转换失败：{str(e)}")
    
    def copy_selected(self):
        """复制选中的文本"""
        try:
            selected_text = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.status_var.set("已复制选中文本到剪贴板")
            # 显示右上角自动消失提示
            self.show_top_right_notification("选中内容已复制到剪贴板！")
        except tk.TclError:
            # 改为自动消失的警告提示
            self.show_top_right_notification("请先选中要复制的文本！")
            self.status_var.set("复制失败：未选中文本")
    
    def copy_all(self):
        """复制全部文本"""
        output_text = self.output_text.get('1.0', tk.END).strip()
        
        if not output_text:
            # 显示右上角自动消失提示
            self.show_top_right_notification("没有可复制的内容！")
            self.status_var.set("复制失败：无内容")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(output_text)
        self.status_var.set("已复制全部文本到剪贴板")
        # 显示右上角自动消失提示
        self.show_top_right_notification("全部内容已复制到剪贴板！")


    def show_top_right_notification(self, message, duration=3000):
        """在右上角显示自动消失的通知"""
        notification = tk.Toplevel(self.root)
        notification.title("")
        notification.resizable(False, False)
        
        # 先隐藏窗口，避免闪烁
        notification.withdraw()
        
        # 移除标题栏
        notification.overrideredirect(True)
        
        # 设置样式 - 改为灰色背景
        notification.configure(bg='#f8f9fa')
        
        # 创建主框架 - 减小垂直内边距
        main_frame = tk.Frame(notification, bg='#f8f9fa', padx=20, pady=8)
        main_frame.pack(fill='both', expand=True)
        
        # 消息文本 - 改为黑色文字，减小字体
        msg_label = tk.Label(
            main_frame,
            text=message,
            font=(self.default_font, 11, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50',
            wraplength=300
        )
        msg_label.pack()
        
        # 添加边框 - 使用更柔和的边框颜色
        notification.configure(relief='solid', bd=1, highlightbackground='#dee2e6')
        
        # 强制更新窗口以获取正确的尺寸
        notification.update_idletasks()
        
        # 计算位置 - 右上角
        width = notification.winfo_reqwidth()
        height = notification.winfo_reqheight()
        
        # 获取主窗口位置和尺寸
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        
        # 计算通知窗口位置（主窗口右上角，稍微向内偏移）
        x = main_x + main_width - width - 20
        y = main_y + 80
        
        # 设置位置
        notification.geometry(f"{width}x{height}+{x}+{y}")
        
        # 创建阴影效果
        shadow = tk.Toplevel(self.root)
        shadow.withdraw()  # 先隐藏阴影
        shadow.overrideredirect(True)
        shadow.configure(bg='#adb5bd')
        shadow.geometry(f"{width}x{height}+{x+2}+{y+2}")
        
        # 现在显示窗口
        notification.deiconify()
        shadow.deiconify()
        
        # 设置置顶和层次
        notification.attributes('-topmost', True)
        shadow.attributes('-topmost', True)
        shadow.lower(notification)
        
        # 淡入动画效果
        def fade_in():
            for alpha in [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
                try:
                    notification.attributes('-alpha', alpha)
                    shadow.attributes('-alpha', alpha * 0.2)
                    notification.update()
                    notification.after(30)
                except tk.TclError:
                    break
        
        # 淡出动画效果
        def fade_out():
            for alpha in [0.9, 0.7, 0.5, 0.3, 0.1, 0.0]:
                try:
                    notification.attributes('-alpha', alpha)
                    shadow.attributes('-alpha', alpha * 0.2)
                    notification.update()
                    notification.after(50)
                except tk.TclError:
                    break
            try:
                notification.destroy()
                shadow.destroy()
            except tk.TclError:
                pass
        
        # 启动淡入动画
        notification.after(10, fade_in)
        
        # 设置自动消失
        notification.after(duration - 500, fade_out)
        
        # 点击通知可立即关闭
        def close_notification(event):
            try:
                notification.destroy()
                shadow.destroy()
            except tk.TclError:
                pass
        
        notification.bind("<Button-1>", close_notification)
        msg_label.bind("<Button-1>", close_notification)    
   

    def clear_all(self):
        """清空所有内容"""
        result = messagebox.askyesno("确认", "确定要清空所有内容吗？")
        if result:
            self.input_text.delete('1.0', tk.END)
            self.output_text.delete('1.0', tk.END)
            self.status_var.set("已清空所有内容")
            # 清空后焦点回到输入框
            self.input_text.focus_set()

    def on_tab_changed(self, event):
        """当用户切换标签页时，检查规则是否变化并更新转换结果"""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        
        if current_tab == "📄 文本转换":
            # 从格式规则页面切换到文本转换页面
            current_input_rules = self.get_input_rules()
            current_output_formats = self.get_output_formats()
            
            # 检查规则是否有变化
            input_rules_changed = self._dict_changed(self.last_input_rules, current_input_rules)
            output_formats_changed = self._dict_changed(self.last_output_formats, current_output_formats)
            
            if input_rules_changed or output_formats_changed:
                # 询问用户是否保存当前配置
                save_result = messagebox.askyesno("格式规则已修改", "格式规则有修改，是否保存为当前配置？")
                if save_result:
                    # 用户选择保存
                    self.save_config_without_message()
                    self.status_var.set("格式规则已更改并保存，正在更新转换结果...")
                    # 更新保存的规则状态
                    self.save_current_rules_state()
                else:
                    # 用户选择不保存，恢复之前的配置
                    self.load_config()
                    self.status_var.set("已恢复之前的配置，正在更新转换结果...")
                
                # 自动重新转换文本
                self.root.after(100, self.auto_convert)  # 使用after确保UI更新完成后再转换
        
        elif current_tab == "⚙️ 格式规则":
            # 切换到格式规则页面时，保存当前规则状态以便后续比较
            self.save_current_rules_state()
    
    def _dict_changed(self, dict1, dict2):
        """比较两个字典是否有变化"""
        if dict1 is None or dict2 is None:
            return True
        
        # 检查键是否相同
        if set(dict1.keys()) != set(dict2.keys()):
            return True
        
        # 检查值是否相同
        for key in dict1:
            if dict1[key] != dict2[key]:
                return True
        
        return False
    
    def save_current_rules_state(self):
        """保存当前的输入和输出规则状态"""
        self.last_input_rules = self.get_input_rules().copy()
        self.last_output_formats = self.get_output_formats().copy()
    
    def load_rules_from_state(self):
        """从保存的状态加载规则"""
        # 这个方法不应该被使用，因为我们现在是通过监测规则变化来自动更新转换结果
        # 保留此方法以兼容现有代码
        pass
    
    def save_config_without_message(self):
        """保存当前配置到文件但不显示消息"""
        try:
            config = {
                'input_rules': {},
                'output_formats': {}
            }
            
            # 保存输入规则的显示值
            for level, var in self.input_vars.items():
                display_value = var.get()
                config['input_rules'][level] = display_value
            
            # 保存输出格式的显示值
            for level, var in self.output_vars.items():
                display_value = var.get()
                config['output_formats'][level] = display_value
            
            # 写入配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            self.status_var.set("配置已保存")
        except Exception as e:
            error_msg = f"保存配置失败：{str(e)}"
            messagebox.showerror("错误", error_msg)
            self.status_var.set(error_msg)
    
    def load_config(self):
        """从文件加载配置"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 加载输入规则
            if 'input_rules' in config:
                for level, display_value in config['input_rules'].items():
                    if level in self.input_vars and display_value:
                        self.input_vars[level].set(display_value)
            
            # 加载输出格式
            if 'output_formats' in config:
                for level, display_value in config['output_formats'].items():
                    if level in self.output_vars and display_value:
                        self.output_vars[level].set(display_value)
            
            # 更新预览
            self.update_preview()
            self.status_var.set("已加载保存的配置")
        except Exception as e:
            error_msg = f"加载配置失败：{str(e)}"
            self.status_var.set(error_msg)
    
    def on_closing(self):
        """窗口关闭时保存配置，但不显示提示"""
        try:
            # 保存配置但不显示提示
            config = {
                'input_rules': {},
                'output_formats': {}
            }
            
            # 保存输入规则的显示值
            for level, var in self.input_vars.items():
                display_value = var.get()
                config['input_rules'][level] = display_value
            
            # 保存输出格式的显示值
            for level, var in self.output_vars.items():
                display_value = var.get()
                config['output_formats'][level] = display_value
            
            # 写入配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception:
            pass  # 如果保存失败，不阻止关闭
        self.root.destroy()
    
    def save_config(self):
        """保存当前配置到文件并显示提示"""
        self.save_config_without_message()
        # 创建自动关闭的提示窗口
        self.show_auto_close_message("配置已保存", "配置已保存，将在下次启动时自动加载", 3000)
    
    def show_auto_close_message(self, title, message, duration=3000):
        """显示自动关闭的消息窗口"""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("400x100")  # 减小高度，因为没有按钮了
        popup.resizable(False, False)
        
        # 设置窗口位置居中
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        
        # 设置样式
        popup.configure(bg='white')
        
        # 添加消息
        msg_label = tk.Label(
            popup,
            text=message,
            font=(self.default_font, 11),
            bg='white',
            fg='#2c3e50',
            wraplength=380
        )
        msg_label.pack(expand=True, pady=(20, 5))
        
        # 添加倒计时标签
        time_left = duration // 1000
        time_var = tk.StringVar(value=f"窗口将在 {time_left} 秒后自动关闭")
        time_label = tk.Label(
            popup,
            textvariable=time_var,
            font=(self.default_font, 9),
            bg='white',
            fg='#7f8c8d'
        )
        time_label.pack(pady=(0, 15))
        
        # 更新倒计时
        def update_countdown():
            nonlocal time_left
            time_left -= 1
            if time_left <= 0:
                popup.destroy()
                return
            time_var.set(f"窗口将在 {time_left} 秒后自动关闭")
            popup.after(1000, update_countdown)
        
        # 启动倒计时
        popup.after(1000, update_countdown)
        
        # 设置自动关闭
        popup.after(duration, popup.destroy)
        
        # 置顶显示
        popup.attributes('-topmost', True)
        
        # 移除窗口装饰（标题栏等），使其看起来更像一个纯提示
        popup.overrideredirect(True)
        
        # 点击任意位置关闭窗口
        popup.bind("<Button-1>", lambda e: popup.destroy())

def main():
    root = tk.Tk()
    app = MarkdownConverterGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # 设置窗口居中
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
