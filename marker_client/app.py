#!/usr/bin/env python3
"""
PDF转Markdown Web应用后端服务器
提供文件管理、ZIP打包和结果列表API
"""
import os
import json
import zipfile
import shutil
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import logging

# 添加父目录到Python路径，以便导入marker模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("marker-web-app")

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
TEMP_FOLDER = 'temp'
ALLOWED_EXTENSIONS = {'pdf'}

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_info(filepath):
    """获取文件信息"""
    stat = os.stat(filepath)
    return {
        'name': os.path.basename(filepath),
        'size': format_file_size(stat.st_size),
        'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
        'path': filepath
    }

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 Bytes"
    
    size_names = ["Bytes", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

@app.route('/')
def index():
    """提供主页面"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory('.', filename)

@app.route('/api/results')
def get_results():
    """获取转换结果列表"""
    try:
        results = []
        for filename in os.listdir(RESULTS_FOLDER):
            if filename.endswith('.zip'):
                filepath = os.path.join(RESULTS_FOLDER, filename)
                if os.path.isfile(filepath):
                    results.append(get_file_info(filepath))
        
        # 按修改时间倒序排列
        results.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        logger.error(f"获取结果列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/results/<filename>')
def download_result(filename):
    """下载结果文件"""
    try:
        # 安全检查：确保文件在RESULTS_FOLDER中
        if not filename.endswith('.zip'):
            return jsonify({'success': False, 'error': '无效的文件类型'}), 400
        
        filepath = os.path.join(RESULTS_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': '文件不存在'}), 404
        
        # 检查文件大小，避免下载空文件
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return jsonify({'success': False, 'error': '文件为空，可能转换失败'}), 400
        
        logger.info(f"下载文件: {filename}, 大小: {file_size} 字节")
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/results/<filename>', methods=['DELETE'])
def delete_result(filename):
    """删除结果文件"""
    try:
        # 安全检查：确保文件在RESULTS_FOLDER中
        if not filename.endswith('.zip'):
            return jsonify({'success': False, 'error': '无效的文件类型'}), 400
        
        filepath = os.path.join(RESULTS_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': '文件不存在'}), 404
        
        os.remove(filepath)
        logger.info(f"已删除文件: {filename}")
        
        return jsonify({
            'success': True,
            'message': f'文件 {filename} 已删除'
        })
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/convert', methods=['POST'])
def convert_pdf():
    """转换PDF文件（通过marker server）"""
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '只支持PDF文件'}), 400
        
        # 获取转换参数
        server_url = request.form.get('server_url', 'http://localhost:8001')
        force_ocr = request.form.get('force_ocr', 'false')
        output_format = request.form.get('output_format', 'markdown')
        page_range = request.form.get('page_range', '')
        
        # 检查是否已有同名结果
        base_name = Path(file.filename).stem
        zip_filename = f"{base_name}.zip"
        zip_path = os.path.join(RESULTS_FOLDER, zip_filename)
        
        if os.path.exists(zip_path):
            return jsonify({
                'success': False,
                'error': f'文件 "{file.filename}" 已转换过，请先删除已有结果再重新转换'
            }), 400
        
        # 保存上传的文件
        upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(upload_path)
        
        # 调用marker server进行转换
        import requests
        
        # 创建临时输出目录
        temp_output_dir = os.path.join(TEMP_FOLDER, base_name)
        os.makedirs(temp_output_dir, exist_ok=True)
        
        try:
            # 直接调用marker server API
            url = f"{server_url.rstrip('/')}/marker/upload"
            
            with open(upload_path, 'rb') as pdf_file:
                files = {'file': (file.filename, pdf_file, 'application/pdf')}
                
                data = {
                    'force_ocr': force_ocr,
                    'output_format': output_format,
                    'paginate_output': 'false'
                }
                
                if page_range:
                    data['page_range'] = page_range
                
                logger.info(f"调用marker server: {url}")
                response = requests.post(url, files=files, data=data, timeout=1800)
                response.raise_for_status()
            
            # 解析响应内容
            response_data = response.json()
            logger.debug(f"API响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 保存原始JSON响应
            with open(os.path.join(temp_output_dir, "raw.json"), 'w', encoding='utf-8') as f:
                f.write(json.dumps(response_data, ensure_ascii=False, indent=2))
            
            # 根据输出格式处理响应
            if output_format == "json":
                # 直接保存整个JSON响应
                content = json.dumps(response_data, indent=2, ensure_ascii=False)
                output_path = os.path.join(temp_output_dir, f"{base_name}.json")
            else:
                # 提取Markdown或HTML内容
                if "output" in response_data:
                    content = response_data["output"]
                elif "markdown" in response_data:  # 处理可能的旧版本响应格式
                    content = response_data["markdown"]
                else:
                    # 尝试在顶层键中查找Markdown内容
                    content = response_data.get("markdown_content", response_data.get("html_content", ""))
                    
                    if not content:
                        logger.warning("无法找到输出内容，使用完整响应作为回退")
                        content = json.dumps(response_data, ensure_ascii=False, indent=2)
                
                output_ext = {
                    "markdown": ".md",
                    "html": ".html"
                }.get(output_format, ".md")
                output_path = os.path.join(temp_output_dir, f"{base_name}{output_ext}")
            
            # 保存转换结果
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"转换结果保存到: {output_path}")
            
            # 保存图像（如果存在）
            if "images" in response_data and isinstance(response_data["images"], dict):
                images_saved = 0
                
                for img_name, img_data in response_data["images"].items():
                    try:
                        # 判断是否是标准的Data URI格式
                        if isinstance(img_data, str) and img_data.startswith("data:image/"):
                            # 处理Base64编码的图片数据（带Data URI前缀）
                            header, data = img_data.split(',', 1)
                            img_format = header.split(';')[0].split('/')[-1]
                            
                            # 确保文件名有正确的扩展名
                            if not img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                                img_name = f"{img_name}.{img_format}"
                            
                            img_path = os.path.join(temp_output_dir, img_name)
                            
                            import base64
                            img_bytes = base64.b64decode(data)
                            
                            with open(img_path, 'wb') as img_file:
                                img_file.write(img_bytes)
                            logger.debug(f"保存图片: {img_path}")
                            images_saved += 1
                        
                        # 判断是否是直接的Base64字符串
                        elif isinstance(img_data, str) and len(img_data) > 100:
                            # 服务器返回的是纯Base64数据，没有Data URI前缀
                            logger.debug(f"处理纯Base64图片: {img_name}")
                            
                            # 尝试确定图片格式
                            if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                                img_format = img_name.split('.')[-1]
                            else:
                                img_format = 'jpeg'  # 默认格式
                                img_name = f"{img_name}.{img_format}"
                            
                            img_path = os.path.join(temp_output_dir, img_name)
                            
                            import base64
                            img_bytes = base64.b64decode(img_data)
                            
                            with open(img_path, 'wb') as img_file:
                                img_file.write(img_bytes)
                            logger.debug(f"保存纯Base64图片: {img_path}")
                            images_saved += 1
                        
                        elif isinstance(img_data, str):
                            # 既不是Data URI也不是纯Base64字符串
                            logger.warning(f"无法识别的图片格式: {img_name}")
                        else:
                            logger.warning(f"图片数据不是字符串类型: {img_name}, 类型: {type(img_data)}")
                    
                    except Exception as e:
                        logger.error(f"处理图片失败 {img_name}: {str(e)}")
                
                if images_saved > 0:
                    logger.info(f"保存了 {images_saved} 张图片")
                else:
                    logger.info("响应中没有有效的图片数据")
            else:
                logger.info("响应中没有图片字段")
            
            # 创建ZIP文件
            if create_zip_from_directory(temp_output_dir, zip_path, base_name):
                logger.info(f"ZIP文件创建成功: {zip_filename}")
            else:
                raise Exception("ZIP文件创建失败")
            
            # 清理临时文件
            shutil.rmtree(temp_output_dir)
            os.remove(upload_path)
            
            return jsonify({
                'success': True,
                'message': f'文件转换成功: {zip_filename}',
                'filename': zip_filename
            })
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_output_dir):
                shutil.rmtree(temp_output_dir)
            if os.path.exists(upload_path):
                os.remove(upload_path)
            raise e
            
    except Exception as e:
        logger.error(f"转换PDF失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def create_zip_from_directory(source_dir, zip_path, base_name):
    """从目录创建ZIP文件"""
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 在ZIP中创建相对路径
                    arcname = os.path.join(base_name, os.path.relpath(file_path, source_dir))
                    zipf.write(file_path, arcname)
        
        # 验证ZIP文件是否创建成功
        if os.path.exists(zip_path):
            zip_size = os.path.getsize(zip_path)
            logger.info(f"ZIP文件创建成功: {zip_path}, 大小: {zip_size} 字节")
            return True
        else:
            logger.error(f"ZIP文件创建失败: {zip_path}")
            return False
    except Exception as e:
        logger.error(f"创建ZIP文件时出错: {str(e)}")
        return False

@app.route('/api/server/test', methods=['POST'])
def test_server_connection():
    """测试marker server连接"""
    try:
        data = request.get_json()
        server_url = data.get('server_url', 'http://localhost:8001')
        
        import requests
        response = requests.get(f"{server_url}/", timeout=10)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': '服务器连接成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'服务器响应状态: {response.status_code}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'无法连接到服务器: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("PDF转Markdown Web应用启动中...")
    print(f"访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务器")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )