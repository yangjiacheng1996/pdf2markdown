#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML表格转Markdown表格工具
将Markdown文件中的HTML表格转换为Markdown格式的表格
"""

import re
import sys
from html.parser import HTMLParser
from typing import List, Dict, Any, Optional


class HTMLTableParser(HTMLParser):
    """HTML表格解析器"""
    
    def __init__(self):
        super().__init__()
        self.reset()
        self.tables = []
        self.current_table = []
        self.current_row = []
        self.current_cell = ""
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.in_th = False
        self.cell_attrs = {}
        
    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
            self.current_table = []
        elif tag == 'tr' and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag in ['td', 'th'] and self.in_tr:
            if tag == 'td':
                self.in_td = True
            else:
                self.in_th = True
            self.current_cell = ""
            # 处理单元格属性（如colspan, rowspan）
            self.cell_attrs = dict(attrs)
            
    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
            if self.current_table:
                self.tables.append(self.current_table.copy())
        elif tag == 'tr' and self.in_table:
            self.in_tr = False
            if self.current_row:
                self.current_table.append(self.current_row.copy())
        elif tag in ['td', 'th'] and self.in_tr:
            # 处理合并单元格
            colspan = int(self.cell_attrs.get('colspan', 1))
            rowspan = int(self.cell_attrs.get('rowspan', 1))
            
            # 清理单元格内容中的多余空格和换行
            cell_content = self.current_cell.strip().replace('\n', ' ')
            cell_content = re.sub(r'\s+', ' ', cell_content)
            
            # 添加单元格和合并单元格的占位符
            self.current_row.append({
                'content': cell_content,
                'colspan': colspan,
                'rowspan': rowspan,
                'is_header': tag == 'th'
            })
            
            # 为colspan添加占位符
            for _ in range(colspan - 1):
                self.current_row.append({
                    'content': '',
                    'colspan': 0,  # 0表示这是合并单元格的占位符
                    'rowspan': rowspan,
                    'is_header': tag == 'th'
                })
            
            self.in_td = False
            self.in_th = False
            
    def handle_data(self, data):
        if self.in_td or self.in_th:
            self.current_cell += data


def html_table_to_markdown(html_table: str) -> str:
    """将HTML表格转换为Markdown表格"""
    
    parser = HTMLTableParser()
    parser.feed(html_table)
    
    if not parser.tables:
        return html_table
    
    table_data = parser.tables[0]
    if not table_data:
        return html_table
    
    # 计算最大列数
    max_cols = max(len(row) for row in table_data)
    
    # 处理行合并
    rowspan_tracker = [{} for _ in range(max_cols)]
    
    # 构建表格数据，处理rowspan
    processed_table = []
    for row_idx, row in enumerate(table_data):
        processed_row = []
        col_idx = 0
        
        while col_idx < max_cols:
            if col_idx < len(row):
                cell = row[col_idx]
                
                # 检查是否有来自上方的rowspan
                if col_idx in rowspan_tracker[col_idx]:
                    processed_row.append("^")
                    col_idx += 1
                    continue
                
                # 处理当前单元格
                if cell['rowspan'] > 1:
                    # 标记后续行需要显示rowspan占位符
                    for r in range(1, cell['rowspan']):
                        if row_idx + r < len(table_data) + 10:  # 安全限制
                            rowspan_tracker[col_idx][row_idx + r] = True
                
                processed_row.append(cell['content'])
                col_idx += cell.get('colspan', 1)
            else:
                processed_row.append("")
                col_idx += 1
        
        processed_table.append(processed_row)
    
    # 生成Markdown表格
    markdown_lines = []
    
    # 表头
    if processed_table:
        header = processed_table[0]
        markdown_lines.append("| " + " | ".join(header) + " |")
        
        # 分隔线
        separator = "| " + " | ".join(["---"] * len(header)) + " |"
        markdown_lines.append(separator)
        
        # 数据行
        for row in processed_table[1:]:
            markdown_lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(markdown_lines)


def convert_html_tables_in_markdown(markdown_content: str) -> str:
    """转换Markdown内容中的所有HTML表格"""
    
    # 匹配HTML表格
    table_pattern = r'<table[^>]*>.*?</table>'
    tables = re.findall(table_pattern, markdown_content, re.DOTALL)
    
    converted_content = markdown_content
    
    for html_table in tables:
        markdown_table = html_table_to_markdown(html_table)
        converted_content = converted_content.replace(html_table, markdown_table)
    
    return converted_content


def process_markdown_file(input_file: str, output_file: Optional[str] = None) -> None:
    """处理Markdown文件，转换其中的HTML表格"""
    
    if output_file is None:
        output_file = input_file
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"正在处理文件: {input_file}")
        print(f"找到 {content.count('<table>')} 个HTML表格")
        
        converted_content = convert_html_tables_in_markdown(content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        
        print(f"转换完成！输出文件: {output_file}")
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        sys.exit(1)


def main():
    """主函数"""
    
    if len(sys.argv) < 2:
        print("用法: python html_table_to_markdown.py <markdown文件> [输出文件]")
        print("示例: python html_table_to_markdown.py input.md output.md")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    
    process_markdown_file(input_file, output_file)


if __name__ == "__main__":
    main()