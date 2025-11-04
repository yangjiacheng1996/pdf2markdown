# 使用官方Python运行时作为基础镜像（使用Python 3.12以支持mineru）
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# 安装系统依赖
RUN apt update && apt upgrade -y && \
    apt install -y vim git curl net-tools wget && \
    apt install -y libgobject-2.0-0 libpango-1.0-0 libpangoft2-1.0-0 && \
    apt install -y libgl1 libglib2.0-0t64 libsm6 libxext6 libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装mineru工具（需要Python 3.10+）
RUN pip install --no-cache-dir mineru

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads results

# 设置文件权限
RUN chmod +x app.py

# 检查mineru是否安装成功
RUN mineru --version || echo "mineru version check failed, but continuing..."

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 启动应用
CMD ["python", "app.py"]