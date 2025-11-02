#!/usr/bin/env python3
"""
PDF to Markdown Converter using marker_server API
Usage: python marker_upload.py -p input.pdf -o output_dir [OPTIONS]
"""
import time
import base64
import argparse
import os
import requests
import json
import logging
import re
from pathlib import Path
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("marker_upload")


def convert_pdf_to_markdown(
        file_path: str,
        output_dir: str,
        server_url: str = "http://localhost:8001",
        force_ocr: str = "False",
        output_format: str = "markdown",
        page_range: str = None,
        paginate_output: bool = False
):
    """将PDF文件转换为Markdown并通过API上传"""

    # 验证文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    # 在output_dir中创建一个与输入文件同名的目录
    output_result_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0])
    os.makedirs(output_result_dir, exist_ok=True)

    # 准备输出文件名
    file_stem = Path(file_path).stem
    output_ext = {
        "markdown": ".md",
        "json": ".json",
        "html": ".html"
    }.get(output_format, ".md")

    output_path = os.path.join(output_result_dir, f"{file_stem}{output_ext}")

    try:
        # 调用API进行转换
        url = f"{server_url.rstrip('/')}/marker/upload"

        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file, 'application/pdf')}

            data = {
                'force_ocr': force_ocr.lower(),
                'output_format': output_format,
                'paginate_output': str(paginate_output).lower()
            }

            if page_range:
                data['page_range'] = page_range

            logger.info(f"Sending request to {url}...")
            # 为post请求添加计时功能
            start_time = time.time()
            response = requests.post(url, files=files, data=data, timeout=1800, proxies={"http": None, "https": None})
            end_time = time.time()
            logger.info(f"post request costs: {end_time - start_time:.2f} seconds")
            response.raise_for_status()

        # 解析响应内容
        response_data = response.json()
        # 先将json保存到output_path中的raw.json中
        with open(os.path.join(output_result_dir, "raw.json"), 'w', encoding='utf-8') as f:
            f.write(json.dumps(response_data, ensure_ascii=False, indent=2))
        logger.debug(f"API response: {json.dumps(response_data, ensure_ascii=False, indent=2)}")

        # 根据输出格式处理响应
        if output_format == "json":
            # 直接保存整个JSON响应
            content = json.dumps(response_data, indent=2, ensure_ascii=False)
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
                    logger.warning("Could not find 'output' key in API response. Using full response as fallback.")
                    content = json.dumps(response_data, ensure_ascii=False, indent=2)

        # 保存转换结果
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"✅ Conversion successful! Output saved to: {output_path}")

        # 保存图像（如果存在）
        if "images" in response_data and isinstance(response_data["images"], dict):
            # images_dir = os.path.join(output_result_dir, "images")
            # os.makedirs(images_dir, exist_ok=True)
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

                        img_path = os.path.join(output_result_dir, img_name)

                        img_bytes = base64.b64decode(data)

                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_bytes)
                        logger.debug(f"Saved image with Data URI: {img_path}")
                        images_saved += 1

                    # 判断是否是直接的Base64字符串
                    elif isinstance(img_data, str) and len(img_data) > 100 and re.match(r'^[a-zA-Z0-9+/=]+$', img_data):
                        # 服务器返回的是纯Base64数据，没有Data URI前缀
                        logger.debug(f"Processing plain Base64 image: {img_name}")

                        # 尝试确定图片格式
                        if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            img_format = img_name.split('.')[-1]
                        else:
                            img_format = 'jpeg'  # 默认格式
                            img_name = f"{img_name}.{img_format}"

                        img_path = os.path.join(output_result_dir, img_name)

                        img_bytes = base64.b64decode(img_data)

                        with open(img_path, 'wb') as img_file:
                            img_file.write(img_bytes)
                        logger.debug(f"Saved plain Base64 image: {img_path}")
                        images_saved += 1

                    elif isinstance(img_data, str):
                        # 既不是Data URI也不是纯Base64字符串
                        logger.warning(f"Unrecognized image format for {img_name}: starts with '{img_data[:50]}'")
                    else:
                        logger.warning(f"Image data for {img_name} is not a string, type: {type(img_data)}")

                except Exception as e:
                    logger.error(f"Failed to process image {img_name}: {str(e)}")

            if images_saved > 0:
                logger.info(f"✅ Saved {images_saved} images to: {output_result_dir}")
            else:
                logger.warning("No valid image data found in response")
        else:
            logger.info("No 'images' field found in response data")

        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Server response: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return False


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(
        description='Convert PDF to Markdown using marker_server API',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # 必需参数
    parser.add_argument('-p', '--path', required=True,
                        help='Input PDF file path')
    parser.add_argument('-o', '--output_dir', required=True,
                        help='Output directory for converted files')

    # API 选项
    parser.add_argument('-s', '--server', default="http://localhost:8001",
                        help='marker_server API URL')

    # 转换选项
    parser.add_argument('--force_ocr', default="True", choices=["True", "False"],
                        help='Force OCR processing even for text-based PDFs')
    parser.add_argument('--output_format', default='markdown',
                        choices=['markdown', 'json', 'html'],
                        help='Output format for converted content')
    parser.add_argument('--page_range',
                        help='Page range to convert (e.g., "1-5", "1,3,5", "1-10,20")')
    parser.add_argument('--paginate_output', action='store_true',
                        help='Add page number separators in output')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    # 执行转换
    success = convert_pdf_to_markdown(
        file_path=args.path,
        output_dir=args.output_dir,
        server_url=args.server,
        force_ocr=args.force_ocr,
        output_format=args.output_format,
        page_range=args.page_range,
        paginate_output=args.paginate_output
    )

    exit(0 if success else 1)


if __name__ == "__main__":
    main()
