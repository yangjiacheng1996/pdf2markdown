#!/usr/bin/env python3
"""
PDF转Markdown Web应用启动脚本
"""
import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ 依赖安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败，请手动运行: pip install -r requirements.txt")
            return False

def main():
    """主函数"""
    print("=" * 50)
    print("PDF转Markdown Web应用")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 启动Flask应用
    print("🚀 启动Web服务器...")
    try:
        from app import app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()