#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown中文格式转换器 - 用户友好版（优化布局）
支持直观的标题格式选择，无需了解正则表达式
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
import json
import os

class MarkdownConverter:
    def __init__(self):
        self.chinese_numbers = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        self.roman_numbers = ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ']
        self.reset_counters()
        
        # 预定义的标题格式库
        self.title_patterns = {
            # 输入格式的正则表达式
            'markdown_h4': {'pattern': r'^####\s*(.+)$', 'name': '#### 标题'},
            'markdown_h3': {'pattern': r'^###\s*(.+)$', 'name': '### 标题'},
            'markdown_h2': {'pattern': r'^##\s*(.+)$', 'name': '## 标题'},
            'markdown_h1': {'pattern': r'^#\s*(.+)$', 'name': '# 标题'},
            'chinese_paren': {'pattern': r'^（([一二三四五六七八九十]+)）\s*(.+)$', 'name': '（一）标题'},
            'chinese_dot': {'pattern': r'^([一二三四五六七八九十]+)、\s*(.+)$', 'name': '一、标题'},
            'number_paren': {'pattern': r'^\((\d+)\)\s*(.+)$', 'name': '(1)标题'},
            'number_dot': {'pattern': r'^(\d+)、\s*(.+)$', 'name': '1、标题'},
            'number_period': {'pattern': r'^(\d+)\.\s*(.+)$', 'name': '1. 标题'},
            'letter_paren': {'pattern': r'^\(([A-Z])\)\s*(.+)$', 'name': '(A)标题'},
            'letter_period': {'pattern': r'^([A-Z])\.\s*(.+)$', 'name': 'A. 标题'},
            'letter_paren_lower': {'pattern': r'^\(([a-z])\)\s*(.+)$', 'name': '(a)标题'},
            'dash': {'pattern': r'^-\s*(.+)$', 'name': '- 标题'},
            'asterisk': {'pattern': r'^\*\s*(.+)$', 'name': '* 标题'},
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
        """清理标题中已有的编号"""
        patterns = [
            r'^[一二三四五六七八九十]+、\s*',
            r'^\d+、\s*',
            r'^[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+、\s*',
            r'^（[一二三四五六七八九十]+）\s*',
            r'^\(\d+\)\s*',
            r'^\([A-Z]\)\s*',
            r'^\d+\.\s+',
            r'^[A-Z]\.\s+',
            r'^[一二三四五六七八九十]+\.\s+',
            r'^\([a-z]\)\s*',
            r'^[-*]\s*',
            r'^\w+\)\s*',
        ]
        
        for pattern in patterns:
            title = re.sub(pattern, '', title)
        
        return title.strip()
    
    def clean_markdown_symbols(self, text):
        """清除Markdown符号，保留文本内容"""
        # 清除标题符号 (# 开头)
        text = re.sub(r'^#+\s*', '', text)
        
        # 清除列表符号 (- * + 开头)
        text = re.sub(r'^[-*+]\s+', '', text)
        
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
        
        # 清除水平线 (--- 或 ***)
        text = re.sub(r'^[-*]{3,}\s*$', '', text)
        
        # 清除引用符号 (> 开头)
        text = re.sub(r'^>\s+', '', text)
        
        # 清除三个井号标记 (### 开头)
        text = re.sub(r'^###\s+', '', text)
        
        # 清除两个星号标记 (**开头或结尾)
        text = re.sub(r'^\*\*', '', text)
        text = re.sub(r'\*\*$', '', text)
        
        # 清除特定的Markdown标记，如示例中的 "### 1. **"
        text = re.sub(r'^###\s+\d+\.\s+\*\*', '', text)
        
        # 清除行内的星号标记
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # 清除行末的星号标记 - 修正：确保能处理文本末尾的星号
        text = re.sub(r'\*\*\s*$', '', text)
        text = re.sub(r'\*$', '', text)  # 清除单个星号结尾
        
        # 清除特定格式，如 "### 4. **地方配套政策（示例）**"
        text = re.sub(r'^###\s+\d+\.\s+\*\*(.*?)\*\*', r'\1', text)
        
        # 清除特定格式，如 "**发布机构**："
        text = re.sub(r'\*\*(.*?)\*\*：', r'\1：', text)
        
        # 清除特定格式，如 "**主要内容**："
        text = re.sub(r'\*\*(.*?)\*\*：', r'\1：', text)
        
        # 清除特定格式，如 "**政策核心目标**"
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # 清除特定格式，如 "**技术升级**："
        text = re.sub(r'\*\*(.*?)\*\*：', r'\1：', text)
        
        # 最后再次检查，确保所有星号都被清除
        text = re.sub(r'\*+', '', text)
        
        return text

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
        
        # 用于跟踪当前段落
        current_paragraph = []
        
        # 用于跟踪列表项的缩进级别
        list_indent_level = 0
        in_list = False
        
        # 用于跟踪标题行
        last_line_was_title = False
        
        for i, line in enumerate(lines):
            original_line = line.strip()
            
            if not original_line:
                # 处理空行
                if current_paragraph:
                    # 如果有积累的段落内容，先添加到结果中
                    converted_lines.append(' '.join(current_paragraph))
                    current_paragraph = []
                
                # 空行结束列表状态
                if in_list:
                    in_list = False
                    list_indent_level = 0
                
                # 不添加空行，完全忽略它们
                continue
            
            # 清除Markdown符号
            cleaned_line = self.clean_markdown_symbols(original_line)
            
            # 检查是否匹配任何输入规则
            matched = False
            for level_name, pattern_key in input_rules.items():
                if pattern_key and pattern_key in self.title_patterns:
                    pattern = self.title_patterns[pattern_key]['pattern']
                    match = re.match(pattern, original_line)
                    
                    if match:
                        # 如果有积累的段落内容，先添加到结果中
                        if current_paragraph:
                            converted_lines.append(' '.join(current_paragraph))
                            current_paragraph = []
                        
                        # 标题结束列表状态
                        in_list = False
                        list_indent_level = 0
                            
                        # 提取标题内容 - 处理不同的匹配组
                        if len(match.groups()) == 1:
                            # 只有标题内容，如：^####\s*(.+)$
                            title = match.group(1).strip()
                        elif len(match.groups()) == 2:
                            # 有编号和标题内容，如：^（([一二三四五六七八九十]+)）\s*(.+)$
                            title = match.group(2).strip()
                        else:
                            title = match.group(-1).strip()  # 取最后一个组
                        
                        # 清理已有的标题编号和Markdown符号
                        clean_title = self.clean_existing_title_numbers(title)
                        clean_title = self.clean_markdown_symbols(clean_title)
                        
                        # 确定级别数字
                        level_num = int(level_name.replace('level', ''))
                        
                        # 生成新的格式化标题
                        converted_title = self.get_formatted_title(level_num, clean_title, output_formats)
                        converted_lines.append(converted_title)
                        last_line_was_title = True
                        matched = True
                        break
            
            if not matched:
                # 检查是否是列表项
                list_match = re.match(r'^([-*+]|\d+\.|[a-zA-Z]\.)\s+', original_line)
                if list_match:
                    # 如果有积累的段落内容，先添加到结果中
                    if current_paragraph:
                        converted_lines.append(' '.join(current_paragraph))
                        current_paragraph = []
                    
                    # 设置列表状态
                    in_list = True
                    last_line_was_title = False
                    
                    # 列表项单独成行
                    converted_lines.append(cleaned_line)
                elif in_list and original_line.startswith('  '):
                    # 这是列表项的子项或续行
                    # 如果前一行是列表项，这行是缩进的，则作为列表项的一部分
                    if converted_lines:
                        # 将这行添加到前一个列表项
                        converted_lines[-1] = converted_lines[-1] + ' ' + cleaned_line
                    last_line_was_title = False
                else:
                    # 普通文本行，累积到当前段落
                    # 如果是段落的第一行，或者前面有内容但不是列表项
                    if not in_list:
                        current_paragraph.append(cleaned_line)
                    else:
                        # 列表状态下的非缩进行，可能是新段落
                        in_list = False
                        current_paragraph.append(cleaned_line)
                    last_line_was_title = False
        
        # 处理最后一个段落（如果有）
        if current_paragraph:
            converted_lines.append(' '.join(current_paragraph))
        
        # 去除所有空行
        result_lines = [line for line in converted_lines if line.strip()]
        
        # 最终结果
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
        
        self.setup_ui()
        
        # 加载配置（如果存在）
        self.load_config()
        
    def setup_ui(self):
        self.root.title("Markdown中文格式转换器 - 用户友好版")
        self.root.geometry("1400x1000")  # 增加窗口宽度
        self.root.configure(bg='#f0f0f0')
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="📝 Markdown中文格式转换器 - 用户友好版", 
            font=('微软雅黑', 18, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        # 主内容框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
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
            font=('微软雅黑', 9)
        )
        status_bar.pack(side='bottom', fill='x')
        
        # 绑定快捷键
        self.root.bind('<Control-Return>', lambda e: self.convert_text())
        self.root.bind('<F5>', lambda e: self.convert_text())
        
        # 绑定标签页切换事件
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # 保存初始规则状态
        self.save_current_rules_state()
        
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
            font=('微软雅黑', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=10,
            pady=10
        )
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 输入文本框
        self.input_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
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
        example_text = """近年来，国家针对大功率充电桩的发展出台了一系列政策文件，以推动新能源汽车充电基础设施的高质量建设。以下是主要的相关政策文件：

### 1. **《关于促进大功率充电设施科学规划建设的通知》（发改办能源〔2025〕632号）**
- **发布机构**：国家发展改革委办公厅、国家能源局综合司、工业和信息化部办公厅、交通运输部办公厅
- **主要内容**：
  - 提出到2027年底，力争全国大功率充电设施（单枪功率≥250kW）超过10万台。
  - 要求新能源车企自建的大功率充电设施网络原则上应无差别开放。
  - 优先改造高速公路服务区利用率超40%的充电设施。
  - 鼓励智能有序充电、光伏/储能配套建设，支持参与电力市场交易。
  - 推动高压碳化硅模块等核心器件国产化，探索兆瓦级充电技术试点。

### 2. **《关于加强新能源汽车与电网融合互动的实施意见》（2024年）**
- **发布机构**：国家发展改革委等四部门
- **主要内容**：
  - 提出到2025年全面实施充电峰谷电价机制，推动新能源汽车参与电网调峰。
  - 支持智能有序充电和车网互动（V2G），鼓励充电设施接入新型负荷管理系统。

### 3. **《关于创新和完善促进绿色发展价格机制的意见》**
- **发布机构**：国家发展改革委
- **主要内容**：
  - 延长电动汽车集中式充换电设施免收容量电费政策至2025年，降低运营成本。

### 4. **地方配套政策（示例）**
- **北京市《2025年第二批先进充电设施示范项目通知》**：
  - 对智能有序充电、V2G、大功率充电设施给予工程投资30%的补助。
- **山西孝县《充换电设施补短板试点奖补资金使用方案》**：
  - 对120kW及以上公共充电桩按25元/kW补贴，V2G、液冷超充等新技术按50元/kW补贴。

### **政策核心目标**
- **技术升级**：推动高压充电、兆瓦级充电技术研发。
- **标准统一**：完善车桩接口标准，促进互取互通。
- **电网协同**：通过智能调度降低充电负荷冲击，提升新能源消纳能力。
- **市场开放**：打破车企充电桩牌照壁垒，提高资源利用率。

如需具体文件原文，可参考国家发改委或地方政府的官方发布渠道。"""
        
        self.input_text.insert('1.0', example_text)
        
        # 初始加载时自动执行一次转换
        self.root.after(100, self.auto_convert)
        
        # 右侧输出区域
        right_frame = tk.LabelFrame(
            content_frame, 
            text="✨ 转换结果", 
            font=('微软雅黑', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=10,
            pady=10
        )
        right_frame.pack(side='right', fill='both', expand=True)
        
        # 复制按钮框架
        copy_frame = tk.Frame(right_frame, bg='white')
        copy_frame.pack(fill='x', pady=(0, 10))
        
        self.copy_selected_btn = tk.Button(
            copy_frame,
            text="📋 复制选中",
            command=self.copy_selected,
            bg='#3498db',
            fg='black',
            font=('微软雅黑', 10, 'bold'),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        self.copy_selected_btn.pack(side='left', padx=(0, 10))
        
        self.copy_all_btn = tk.Button(
            copy_frame,
            text="📄 复制全部",
            command=self.copy_all,
            bg='#27ae60',
            fg='black',
            font=('微软雅黑', 10, 'bold'),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        self.copy_all_btn.pack(side='left')
        
        # 输出文本框
        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=('微软雅黑', 11),
            bg='#f8f9fa',
            fg='#333333',
            insertbackground='#2c3e50',
            selectbackground='#3498db',
            selectforeground='white',
            state='normal'
        )
        self.output_text.pack(fill='both', expand=True)
        
        # 格式设置面板
        self.setup_format_settings(parent)
    
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
            font=('微软雅黑', 12, 'bold'),
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
            font=('微软雅黑', 12, 'bold'),
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
            font=('微软雅黑', 12, 'bold'),
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
        # 添加保存配置按钮
        save_config_btn = tk.Button(
            parent,
            text="💾 保存当前配置",
            command=self.save_config,
            bg='#2ecc71',
            fg='black',
            font=('微软雅黑', 11, 'bold'),
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        save_config_btn.pack(fill='x', pady=(0, 10))
        
        # 实时预览区域
        preview_frame = tk.LabelFrame(
            parent,
            text="👁️ 实时预览对比",
            font=('微软雅黑', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        preview_frame.pack(fill='both', expand=False, pady=0)
        
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
        # before_frame.pack(side='left', fill='both', expand=True, padx=(0, 2))
        before_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 2))
        
        self.preview_before_text = scrolledtext.ScrolledText(
            before_frame,
            wrap=tk.WORD,
            font=('微软雅黑', 10),
            bg='#fff3f3',
            fg='#333333',
            height=10,  # 进一步减小高度
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
        # after_frame.pack(side='left', fill='both', expand=True, padx=(2, 0))
        after_frame.grid(row=0, column=1, sticky='nsew', padx=(2, 0))
        
        self.preview_after_text = scrolledtext.ScrolledText(
            after_frame,
            wrap=tk.WORD,
            font=('微软雅黑', 10),
            bg='#f3fff3',
            fg='#333333',
            height=10,  # 进一步减小高度
            state='normal'
        )
        self.preview_after_text.pack(fill='both', expand=True)
        
        # 格式对照表区域
        reference_frame = tk.LabelFrame(
            parent,
            text="📋 格式对照表",
            font=('微软雅黑', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=10
        )
        reference_frame.pack(fill='x', pady=(10, 0))
        
        # 对照表内容
        reference_text = """常用格式对照：

输入格式示例           →    输出格式示例
─────────────────────────────────────
（一）项目概述         →    一、项目概述
（二）实施方案         →    二、实施方案

1、主要内容           →    （一）主要内容  
2、具体措施           →    （二）具体措施

- 重点工作            →    1. 重点工作
- 关键环节            →    2. 关键环节

* 详细说明            →    (1)详细说明
* 注意事项            →    (2)注意事项"""
        
        reference_label = tk.Label(
            reference_frame,
            text=reference_text,
            font=('Consolas', 10),
            bg='white',
            fg='#2c3e50',
            justify='left'
        )
        reference_label.pack(anchor='w')
        
        # 初始化预览
        self.update_preview()
    
    def update_preview(self):
        """更新预览内容 - 左右对比版本"""
        try:
            # 获取当前设置
            input_rules = self.get_input_rules()
            output_formats = self.get_output_formats()
            
            # 示例文本
            sample_text = """近年来，国家针对大功率充电桩的发展出台了一系列政策文件，以推动新能源汽车充电基础设施的高质量建设。以下是主要的相关政策文件：

### 1. **《关于促进大功率充电设施科学规划建设的通知》（发改办能源〔2025〕632号）**
- **发布机构**：国家发展改革委办公厅、国家能源局综合司、工业和信息化部办公厅、交通运输部办公厅
- **主要内容**：
  - 提出到2027年底，力争全国大功率充电设施（单枪功率≥250kW）超过10万台。
  - 要求新能源车企自建的大功率充电设施网络原则上应无差别开放。
  - 优先改造高速公路服务区利用率超40%的充电设施。
  - 鼓励智能有序充电、光伏/储能配套建设，支持参与电力市场交易。
  - 推动高压碳化硅模块等核心器件国产化，探索兆瓦级充电技术试点。

### 2. **《关于加强新能源汽车与电网融合互动的实施意见》（2024年）**
- **发布机构**：国家发展改革委等四部门
- **主要内容**：
  - 提出到2025年全面实施充电峰谷电价机制，推动新能源汽车参与电网调峰。
  - 支持智能有序充电和车网互动（V2G），鼓励充电设施接入新型负荷管理系统。

如需具体文件原文，可参考国家发改委或地方政府的官方发布渠道。"""
            
            # 更新转换前的内容
            self.preview_before_text.delete('1.0', tk.END)
            self.preview_before_text.insert('1.0', sample_text)
            
            # 更新转换后的内容
            if input_rules:
                # 进行转换
                result = self.converter.convert_text(sample_text, input_rules, output_formats)
                self.preview_after_text.delete('1.0', tk.END)
                self.preview_after_text.insert('1.0', result)
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
                font=('微软雅黑', 10, 'bold'),
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
                font=('微软雅黑', 10)
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
                font=('微软雅黑', 9),
                padx=10,
                pady=2
            )
            preview_btn.pack(side='left', padx=5)
        
        # 设置完所有默认值后保存初始状态
        if not self.rules_initialized:
            self.root.after(100, self.save_current_rules_state)
            self.rules_initialized = True
    
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
                font=('微软雅黑', 10, 'bold'),
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
                font=('微软雅黑', 10)
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
                font=('微软雅黑', 9),
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
                    'level1': '一、二、三、',
                    'level2': '（一）（二）（三）',
                    'level3': '1. 2. 3.',
                    'level4': '(1)(2)(3)'
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
                    'level1': '一、二、三、',
                    'level2': '（一）（二）（三）',
                    'level3': '1. 2. 3.',
                    'level4': '(1)(2)(3)'
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
                    'level1': '1、2、3、',
                    'level2': '(1)(2)(3)',
                    'level3': '1. 2. 3.',
                    'level4': '(a)(b)(c)'
                }
            }
        ]
        
        # 创建网格布局来更好地显示预设按钮
        for i, preset in enumerate(presets):
            preset_container = tk.Frame(parent, bg='white', relief='raised', bd=1)
            preset_container.pack(fill='x', pady=8, padx=5)
            
            # 预设按钮
            btn = tk.Button(
                preset_container,
                text=f"🎯 {preset['name']}",
                command=lambda p=preset: self.apply_preset(p),
                bg='#3498db',
                fg='black',
                font=('微软雅黑', 11, 'bold'),
                padx=20,
                pady=10,
                width=18
            )
            btn.pack(side='left', padx=10, pady=5)
            
            # 描述区域
            desc_frame = tk.Frame(preset_container, bg='white')
            desc_frame.pack(side='left', fill='both', expand=True, padx=10)
            
            desc_label = tk.Label(
                desc_frame,
                text=f"格式: {preset['description']}",
                font=('微软雅黑', 10, 'bold'),
                bg='white',
                fg='#27ae60',
                anchor='w'
            )
            desc_label.pack(anchor='w')
            
            # 详细说明
            detail_text = f"输入: {' | '.join(preset['input'].values())[:50]}..."
            detail_label = tk.Label(
                desc_frame,
                text=detail_text,
                font=('微软雅黑', 9),
                bg='white',
                fg='#7f8c8d',
                anchor='w'
            )
            detail_label.pack(anchor='w')
    
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
            messagebox.showwarning("警告", "未找到对应的格式信息")
    
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
            messagebox.showwarning("警告", "未找到示例")
    
    def apply_preset(self, preset):
        """应用预设配置"""
        # 设置输入格式
        for level, format_name in preset['input'].items():
            if level in self.input_vars:
                self.input_vars[level].set(format_name)
        
        # 设置输出格式
        for level, format_name in preset['output'].items():
            if level in self.output_vars:
                self.output_vars[level].set(format_name)
        
        # 更新预览
        if hasattr(self, 'update_preview'):
            self.update_preview()
        
        self.status_var.set(f"已应用预设：{preset['name']}")
        messagebox.showinfo("成功", f"已应用预设配置：{preset['name']}")
    
    def setup_format_settings(self, parent):
        """设置快速转换按钮"""
        quick_frame = tk.LabelFrame(
            parent,
            text="🚀 操作区域",
            font=('微软雅黑', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        quick_frame.pack(fill='x', padx=10, pady=(20, 0))
        
        # 按钮框架
        button_frame = tk.Frame(quick_frame, bg='white')
        button_frame.pack(fill='x')
        
        # 清空按钮
        self.clear_btn = tk.Button(
            button_frame,
            text="🗑️ 清空内容",
            command=self.clear_all,
            bg='#95a5a6',
            fg='black',
            font=('微软雅黑', 12, 'bold'),
            relief='flat',
            padx=30,
            pady=10,
            cursor='hand2'
        )
        self.clear_btn.pack(side='left')
        
        # 说明文本
        tip_text = "💡 提示：输入文本后会自动转换，请先在【格式规则】页面设置输入和输出格式"
        tip_label = tk.Label(
            quick_frame,
            text=tip_text,
            font=('微软雅黑', 10),
            bg='white',
            fg='#e67e22'
        )
        tip_label.pack(pady=(10, 0), side='left', padx=(20, 0))
        
        # 鼠标悬停效果
        self.setup_hover_effects()
    
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
            messagebox.showwarning("警告", "请先输入要转换的文本！")
            self.status_var.set("转换失败：输入为空")
            return
        
        try:
            input_rules = self.get_input_rules()
            output_formats = self.get_output_formats()
            
            if not input_rules:
                warning_msg = "请先在【格式规则】页面设置至少一个输入格式！"
                messagebox.showwarning("警告", warning_msg)
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
            messagebox.showinfo("成功", "选中文本已复制到剪贴板！")
        except tk.TclError:
            messagebox.showwarning("警告", "请先选中要复制的文本！")
            self.status_var.set("复制失败：未选中文本")
    
    def copy_all(self):
        """复制全部文本"""
        output_text = self.output_text.get('1.0', tk.END).strip()
        
        if not output_text:
            messagebox.showwarning("警告", "没有可复制的内容！")
            self.status_var.set("复制失败：无内容")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(output_text)
        self.status_var.set("已复制全部文本到剪贴板")
        messagebox.showinfo("成功", "全部内容已复制到剪贴板！")
    
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
                self.status_var.set("格式规则已更改，正在更新转换结果...")
                # 更新保存的规则状态
                self.last_input_rules = current_input_rules.copy()
                self.last_output_formats = current_output_formats.copy()
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
    
    def save_config(self):
        """保存当前配置到文件"""
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
            
            # 创建自动关闭的提示窗口
            self.show_auto_close_message("配置已保存", "配置已保存，将在下次启动时自动加载", 3000)
        except Exception as e:
            error_msg = f"保存配置失败：{str(e)}"
            messagebox.showerror("错误", error_msg)
            self.status_var.set(error_msg)
    
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
            font=('微软雅黑', 11),
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
            font=('微软雅黑', 9),
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