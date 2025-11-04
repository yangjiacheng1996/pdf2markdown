#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF到Markdown转换一体化客户端
集成mineru命令和HTML表格转换功能

功能特性:
1. 一键将PDF转换为Markdown格式
2. 支持HTML表格和Markdown表格格式
3. 自动检测虚拟环境中的mineru命令
4. 完整的错误处理和日志输出
5. 支持多种OCR语言和配置选项

使用示例:
  python mineru_client.py -p document.pdf -o ./output -u http://172.27.213.31:30000
  python mineru_client.py -p doc.pdf -o ./md -u http://localhost:30000 -m text -t html
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List

# 添加当前目录到Python路径，确保可以导入本地模块
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入现有的表格转换功能
try:
    from html_table_to_markdown import convert_html_tables_in_markdown
except ImportError as e:
    print(f"错误: 无法导入html_table_to_markdown模块: {e}")
    print("请确保html_table_to_markdown.py在同一目录下")
    sys.exit(1)


class MineruClient:
    """PDF到Markdown转换客户端"""
    
    def __init__(self):
        self.mineru_cmd = "mineru"
        # 检查mineru命令是否在虚拟环境中
        if hasattr(sys, 'prefix') and sys.prefix:
            venv_mineru = os.path.join(sys.prefix, "Scripts", "mineru.exe")
            if os.path.exists(venv_mineru):
                self.mineru_cmd = venv_mineru
        
    def check_mineru_available(self) -> bool:
        """检查mineru命令是否可用"""
        try:
            result = subprocess.run([self.mineru_cmd, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            return False
    
    def build_mineru_command(self, args: argparse.Namespace) -> List[str]:
        """构建mineru命令参数列表"""
        cmd = [self.mineru_cmd]
        
        # 必需参数 - 直接传递路径，subprocess会正确处理
        cmd.extend(["-p", args.pdf_path])
        cmd.extend(["-o", args.output_dir])
        
        # 后端设置为vlm-http-client（必需参数）
        cmd.extend(["-b", "vlm-http-client"])
        cmd.extend(["-u", args.url])
        
        # 方法参数（text或ocr）
        cmd.extend(["-m", args.method])
        
        # 可选参数
        if hasattr(args, 'lang') and args.lang:
            cmd.extend(["-l", args.lang])
        
        if hasattr(args, 'start_page') and args.start_page is not None:
            cmd.extend(["-s", str(args.start_page)])
        
        if hasattr(args, 'end_page') and args.end_page is not None:
            cmd.extend(["-e", str(args.end_page)])
        
        if hasattr(args, 'formula') and args.formula is not None:
            cmd.extend(["-f", str(args.formula).lower()])
        
        if hasattr(args, 'table') and args.table is not None:
            cmd.extend(["--table", str(args.table).lower()])
        
        if hasattr(args, 'device') and args.device:
            cmd.extend(["-d", args.device])
        
        return cmd
    
    def run_mineru_conversion(self, cmd: List[str]) -> bool:
        """运行mineru转换命令"""
        try:
            print(f"运行mineru命令: {' '.join(cmd)}")
            # 使用shell=False确保参数正确处理，subprocess会自动处理包含空格的路径
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, shell=False)
            
            if result.returncode == 0:
                print("mineru转换成功完成")
                if result.stdout:
                    print(f"mineru输出: {result.stdout}")
                return True
            else:
                print(f"mineru转换失败，返回码: {result.returncode}")
                if result.stderr:
                    print(f"错误信息: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("mineru转换超时（60分钟）")
            return False
        except Exception as e:
            print(f"运行mineru命令时发生异常: {e}")
            return False
    
    def find_output_markdown_file(self, pdf_path: str, output_dir: str) -> Optional[str]:
        """查找输出的markdown文件，支持递归搜索子目录"""
        pdf_name = Path(pdf_path).stem
        
        # 首先尝试常见的mineru输出目录结构
        possible_paths = [
            # 直接在当前目录
            os.path.join(output_dir, f"{pdf_name}.md"),
            os.path.join(output_dir, f"{Path(pdf_path).name}.md"),
            # mineru常见的子目录结构
            os.path.join(output_dir, pdf_name, "vlm", f"{pdf_name}.md"),
            os.path.join(output_dir, pdf_name, "text", f"{pdf_name}.md"),
            os.path.join(output_dir, pdf_name, "ocr", f"{pdf_name}.md"),
        ]
        
        # 检查这些可能的路径
        for possible_path in possible_paths:
            if os.path.exists(possible_path):
                print(f"在预定义路径找到markdown文件: {possible_path}")
                return possible_path
        
        # 递归搜索整个输出目录
        print(f"在输出目录中递归搜索markdown文件: {output_dir}")
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.md'):
                    md_path = os.path.join(root, file)
                    print(f"找到markdown文件: {md_path}")
                    return md_path
        
        print(f"未找到任何markdown文件，已搜索目录: {output_dir}")
        return None
    
    def convert_tables_to_markdown(self, input_file: str, output_file: Optional[str] = None) -> bool:
        """将HTML表格转换为Markdown格式"""
        if output_file is None:
            output_file = input_file
        
        try:
            print(f"开始转换表格格式: {input_file}")
            
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统计HTML表格数量
            table_count = content.count('<table')
            print(f"找到 {table_count} 个HTML表格")
            
            if table_count > 0:
                converted_content = convert_html_tables_in_markdown(content)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
                
                print(f"表格转换完成，输出文件: {output_file}")
            else:
                print("未找到HTML表格，无需转换")
                if input_file != output_file:
                    shutil.copy2(input_file, output_file)
            
            return True
            
        except Exception as e:
            print(f"表格转换失败: {e}")
            return False
    
    def process_pdf_to_markdown(self, args: argparse.Namespace) -> bool:
        """处理PDF到Markdown的完整流程"""
        
        # 检查mineru是否可用
        if not self.check_mineru_available():
            print(f"错误: mineru命令不可用，请确保已安装并在PATH中或虚拟环境中")
            return False
        
        # 检查输入文件是否存在
        if not os.path.exists(args.pdf_path):
            print(f"错误: PDF文件不存在: {args.pdf_path}")
            return False
        
        # 创建输出目录（如果不存在）
        os.makedirs(args.output_dir, exist_ok=True)
        
        # 构建并运行mineru命令
        cmd = self.build_mineru_command(args)
        if not self.run_mineru_conversion(cmd):
            return False
        
        # 查找输出的markdown文件
        md_file = self.find_output_markdown_file(args.pdf_path, args.output_dir)
        if not md_file:
            print("错误: 无法找到输出的markdown文件")
            return False
        
        print(f"找到输出的markdown文件: {md_file}")
        
        # 如果需要转换表格格式
        if args.table_format == 'markdown':
            return self.convert_tables_to_markdown(md_file)
        else:
            print(f"表格格式设置为 {args.table_format}，跳过表格转换")
            return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PDF到Markdown转换一体化客户端",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python mineru_client.py -p document.pdf -o ./output -u http://172.27.213.31:30000
  python mineru_client.py -p doc.pdf -o ./md -u http://localhost:30000 -m text -t html
        """
    )
    
    # 必需参数
    parser.add_argument("-p", "--pdf-path", required=True,
                       help="PDF文件路径")
    parser.add_argument("-o", "--output-dir", required=True,
                       help="Markdown输出目录")
    parser.add_argument("-u", "--url", required=True,
                       help="mineru-vllm-server的URL")
    
    # 可选参数
    parser.add_argument("-m", "--method", default="ocr",
                       choices=["txt", "ocr"],
                       help="文本模式或OCR模式，默认: ocr")
    parser.add_argument("-t", "--table-format", default="markdown",
                       choices=["html", "markdown"],
                       help="表格格式，html或markdown，默认: markdown")
    
    # mineru的其他可选参数
    parser.add_argument("-l", "--lang", 
                       choices=["ch", "ch_server", "ch_lite", "en", "korean", "japan", 
                               "chinese_cht", "ta", "te", "ka", "th", "el", "latin", 
                               "arabic", "east_slavic", "cyrillic", "devanagari"],
                       help="PDF语言，用于提高OCR精度")
    parser.add_argument("-s", "--start-page", type=int,
                       help="起始页码（从0开始）")
    parser.add_argument("-e", "--end-page", type=int,
                       help="结束页码（从0开始）")
    parser.add_argument("-f", "--formula", type=bool,
                       help="启用公式解析")
    parser.add_argument("--table", type=bool,
                       help="启用表格解析")
    parser.add_argument("-d", "--device",
                       help="设备模式，如cpu, cuda, cuda:0等")
    
    args = parser.parse_args()
    
    client = MineruClient()
    success = client.process_pdf_to_markdown(args)
    
    if success:
        print("PDF到Markdown转换完成！")
        sys.exit(0)
    else:
        print("PDF到Markdown转换失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()