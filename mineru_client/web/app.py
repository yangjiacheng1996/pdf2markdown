#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mineru Web界面后端服务器
提供PDF转Markdown的Web界面API
"""

import os
import sys
import json
import zipfile
import tempfile
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging

# 添加当前目录到Python路径，确保可以导入本地模块
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 导入mineru客户端
try:
    from mineru_client import MineruClient
except ImportError as e:
    print(f"警告: 无法导入mineru_client: {e}")
    print("尝试从父目录导入...")
    # 添加父目录到路径
    parent_dir = current_dir.parent
    sys.path.insert(0, str(parent_dir))
    try:
        from mineru_client import MineruClient
    except ImportError:
        print("无法导入mineru_client，将使用子进程方式")
        MineruClient = None

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
OUTPUT_FOLDER = Path(__file__).parent / 'results'
ALLOWED_EXTENSIONS = {'pdf'}

# 创建必要的目录
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / 'server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file_path):
    """获取文件大小并格式化"""
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def create_zip_from_output(pdf_name, output_dir, zip_path):
    """将输出目录打包为zip文件"""
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 在zip中创建相对路径
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
        
        logger.info(f"成功创建zip文件: {zip_path}")
        return True
    except Exception as e:
        logger.error(f"创建zip文件失败: {e}")
        return False

def sanitize_filename(filename):
    """清理文件名，移除可能引起问题的字符"""
    # 移除路径分隔符和引号
    invalid_chars = ['/', '\\', '"', "'", '|', '<', '>', '*', '?']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def run_mineru_conversion(pdf_path, output_dir, server_url, **kwargs):
    """运行mineru转换"""
    try:
        # 构建命令行参数 - 直接运行脚本文件而不是模块
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        mineru_script = parent_dir / "mineru_client.py"
        
        if not mineru_script.exists():
            # 如果父目录没有，尝试当前目录
            mineru_script = current_dir / "mineru_client.py"
        
        if not mineru_script.exists():
            error_msg = f"找不到mineru_client.py脚本: {mineru_script}"
            logger.error(error_msg)
            return False, error_msg
        
        # 构建命令参数 - 直接使用路径，不要添加引号
        cmd = [
            sys.executable, 
            str(mineru_script),
            "-p", pdf_path,  # 直接传递路径，subprocess会正确处理
            "-o", output_dir,  # 直接传递路径，subprocess会正确处理
            "-u", server_url
        ]
        
        # 添加可选参数
        if kwargs.get('method'):
            cmd.extend(["-m", kwargs['method']])
        if kwargs.get('table_format'):
            cmd.extend(["-t", kwargs['table_format']])
        if kwargs.get('language'):
            cmd.extend(["-l", kwargs['language']])
        if kwargs.get('device'):
            cmd.extend(["-d", kwargs['device']])
        if kwargs.get('start_page') is not None:
            cmd.extend(["-s", str(kwargs['start_page'])])
        if kwargs.get('end_page') is not None:
            cmd.extend(["-e", str(kwargs['end_page'])])
        if kwargs.get('formula'):
            cmd.extend(["-f", kwargs['formula']])
        if kwargs.get('table'):
            cmd.extend(["--table", kwargs['table']])
        
        logger.info(f"运行mineru命令: {' '.join(cmd)}")
        
        # 运行转换 - 使用shell=False确保参数正确处理
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, shell=False)
        
        if result.returncode == 0:
            logger.info("mineru转换成功完成")
            if result.stdout:
                logger.info(f"mineru输出: {result.stdout}")
            return True, result.stdout
        else:
            logger.error(f"mineru转换失败，返回码: {result.returncode}")
            if result.stderr:
                logger.error(f"错误信息: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        error_msg = "mineru转换超时（60分钟）"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"运行mineru命令时发生异常: {e}"
        logger.error(error_msg)
        return False, error_msg

@app.route('/api/server/test', methods=['POST'])
def test_server_connection():
    """测试mineru服务器连接"""
    try:
        data = request.get_json()
        server_url = data.get('server_url')
        
        if not server_url:
            return jsonify({'success': False, 'error': '服务器地址不能为空'})
        
        # 构建健康检查URL - 直接测试mineru服务器的/health端点
        import requests
        from urllib.parse import urljoin
        
        # 确保URL格式正确
        if not server_url.startswith(('http://', 'https://')):
            server_url = 'http://' + server_url
        
        # 构建健康检查端点URL
        health_url = urljoin(server_url, '/health')
        
        try:
            # 直接测试mineru服务器的健康检查端点
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                return jsonify({'success': True, 'message': '服务器连接正常'})
            else:
                return jsonify({
                    'success': False, 
                    'error': f'服务器返回状态码: {response.status_code}，期望200'
                })
        except requests.exceptions.ConnectTimeout:
            return jsonify({'success': False, 'error': '连接超时，请检查服务器地址和端口'})
        except requests.exceptions.ConnectionError:
            return jsonify({'success': False, 'error': '无法连接到服务器，请检查网络连接和服务器状态'})
        except requests.exceptions.RequestException as e:
            return jsonify({'success': False, 'error': f'连接测试失败: {str(e)}'})
            
    except Exception as e:
        logger.error(f"测试服务器连接时出错: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/convert', methods=['POST'])
def convert_pdf():
    """转换PDF文件"""
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '只支持PDF文件'})
        
        # 获取参数
        server_url = request.form.get('server_url')
        method = request.form.get('method', 'ocr')
        table_format = request.form.get('table_format', 'markdown')
        language = request.form.get('language')
        device = request.form.get('device')
        start_page = request.form.get('start_page')
        end_page = request.form.get('end_page')
        formula = request.form.get('formula', 'false')
        table = request.form.get('table', 'true')
        
        if not server_url:
            return jsonify({'success': False, 'error': '服务器地址不能为空'})
        
        # 清理文件名，移除可能引起问题的字符
        safe_filename = sanitize_filename(file.filename)
        pdf_name = Path(safe_filename).stem
        
        # 检查是否已存在同名结果
        zip_filename = f"{pdf_name}.zip"
        zip_path = OUTPUT_FOLDER / zip_filename
        
        if zip_path.exists():
            return jsonify({
                'success': False, 
                'error': f'文件 "{file.filename}" 已转换过，请先删除已有结果再重新转换'
            })
        
        # 保存上传的文件（使用安全的文件名）
        upload_path = UPLOAD_FOLDER / safe_filename
        file.save(upload_path)
        logger.info(f"文件已保存: {upload_path}")
        
        # 在results目录下创建输出目录 - 移除自动添加的_output后缀
        # 直接使用pdf_name作为目录名，让mineru_client.py自己处理输出结构
        output_dir = OUTPUT_FOLDER / pdf_name
        output_dir.mkdir(exist_ok=True)
        
        # 运行转换
        success, output = run_mineru_conversion(
            str(upload_path),
            str(output_dir),  # 使用results目录下的子目录
            server_url,
            method=method,
            table_format=table_format,
            language=language,
            device=device,
            start_page=start_page,
            end_page=end_page,
            formula=formula,
            table=table
        )
        
        if success:
            # 检查是否有输出文件
            md_files = list(output_dir.rglob("*.md"))
            if not md_files:
                # 清理上传的文件和输出目录
                upload_path.unlink(missing_ok=True)
                shutil.rmtree(output_dir, ignore_errors=True)
                return jsonify({'success': False, 'error': '转换成功但未找到输出文件'})
            
            # 打包输出文件
            if create_zip_from_output(pdf_name, str(output_dir), zip_path):
                # 清理上传的文件和输出目录
                upload_path.unlink(missing_ok=True)
                shutil.rmtree(output_dir, ignore_errors=True)
                
                return jsonify({
                    'success': True,
                    'message': f'文件 "{file.filename}" 转换成功',
                    'zip_file': zip_filename
                })
            else:
                # 清理上传的文件和输出目录
                upload_path.unlink(missing_ok=True)
                shutil.rmtree(output_dir, ignore_errors=True)
                return jsonify({'success': False, 'error': '打包输出文件失败'})
        else:
            # 清理上传的文件和输出目录
            upload_path.unlink(missing_ok=True)
            shutil.rmtree(output_dir, ignore_errors=True)
            return jsonify({'success': False, 'error': f'转换失败: {output}'})
            
    except Exception as e:
        logger.error(f"转换PDF时出错: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/results', methods=['GET'])
def get_results():
    """获取转换结果列表"""
    try:
        results = []
        
        for file_path in OUTPUT_FOLDER.glob("*.zip"):
            stat = file_path.stat()
            results.append({
                'name': file_path.name,
                'size': get_file_size(file_path),
                'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'path': str(file_path)
            })
        
        # 按修改时间倒序排列
        results.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        logger.error(f"获取结果列表时出错: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/results/<filename>', methods=['GET'])
def download_result(filename):
    """下载转换结果"""
    try:
        file_path = OUTPUT_FOLDER / filename
        
        if not file_path.exists():
            return jsonify({'success': False, 'error': '文件不存在'})
        
        # 安全检查：确保文件在输出目录内
        if not file_path.resolve().is_relative_to(OUTPUT_FOLDER.resolve()):
            return jsonify({'success': False, 'error': '非法文件路径'})
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"下载文件时出错: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/results/<filename>', methods=['DELETE'])
def delete_result(filename):
    """删除转换结果"""
    try:
        file_path = OUTPUT_FOLDER / filename
        
        if not file_path.exists():
            return jsonify({'success': False, 'error': '文件不存在'})
        
        # 安全检查：确保文件在输出目录内
        if not file_path.resolve().is_relative_to(OUTPUT_FOLDER.resolve()):
            return jsonify({'success': False, 'error': '非法文件路径'})
        
        file_path.unlink()
        logger.info(f"已删除文件: {filename}")
        
        return jsonify({'success': True, 'message': f'文件 {filename} 已删除'})
        
    except Exception as e:
        logger.error(f"删除文件时出错: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/')
def index():
    """提供前端页面"""
    return send_file('index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    try:
        return send_file(filename)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    logger.info("启动Mineru Web服务器...")
    logger.info(f"上传目录: {UPLOAD_FOLDER}")
    logger.info(f"输出目录: {OUTPUT_FOLDER}")
    
    # 确保必要的目录存在
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)