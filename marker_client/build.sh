#!/bin/bash

# PDF转Markdown Web应用 Docker构建脚本

echo "开始构建PDF转Markdown Web应用Docker镜像..."

# 设置镜像标签
IMAGE_NAME="pdf-to-markdown-webapp"
TAG="latest"

# 构建Docker镜像
docker build -t $IMAGE_NAME:$TAG .

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo "✅ Docker镜像构建成功: $IMAGE_NAME:$TAG"
    echo ""
    echo "运行以下命令启动容器:"
    echo "  docker run -d -p 5000:5000 --name pdf-converter $IMAGE_NAME:$TAG"
    echo ""
    echo "或者使用docker-compose启动:"
    echo "  docker-compose up -d"
else
    echo "❌ Docker镜像构建失败"
    exit 1
fi