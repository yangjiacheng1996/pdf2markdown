# PDF转Markdown Web应用 - Docker部署指南

本文档介绍如何使用Docker容器化部署PDF转Markdown Web应用。

## 项目概述

这是一个基于Flask的Web应用，提供PDF转Markdown的Web界面，支持：
- 拖拽上传PDF文件
- 实时转换进度显示
- 转换结果管理（下载、删除）
- 与Marker Server集成

## 快速开始

### 方式一：使用Docker Compose（推荐）

1. **构建并启动容器**
   ```bash
   docker-compose up -d
   ```

2. **查看运行状态**
   ```bash
   docker-compose ps
   ```

3. **查看日志**
   ```bash
   docker-compose logs -f
   ```

4. **停止容器**
   ```bash
   docker-compose down
   ```

### 方式二：使用Docker命令

1. **构建镜像**
   ```bash
   docker build -t pdf-to-markdown-webapp .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     -p 5000:5000 \
     --name pdf-converter \
     -v $(pwd)/uploads:/app/uploads \
     -v $(pwd)/results:/app/results \
     -v $(pwd)/temp:/app/temp \
     pdf-to-markdown-webapp
   ```

3. **查看运行状态**
   ```bash
   docker ps
   ```

4. **查看日志**
   ```bash
   docker logs -f pdf-converter
   ```

5. **停止容器**
   ```bash
   docker stop pdf-converter
   docker rm pdf-converter
   ```

### 方式三：使用构建脚本

1. **构建镜像**
   ```bash
   ./build.sh
   ```

2. **运行容器**
   ```bash
   docker run -d -p 5000:5000 --name pdf-converter pdf-to-markdown-webapp:latest
   ```

## 访问应用

容器启动后，在浏览器中访问：http://localhost:5000

## 配置说明

### 环境变量

- `FLASK_ENV`: 运行环境（默认：production）
- `FLASK_APP`: 主应用文件（默认：app.py）

### 端口映射

- 容器内部端口：5000
- 主机映射端口：5000（可在docker-compose.yml中修改）

### 数据持久化

以下目录通过卷挂载实现数据持久化：

- `uploads/`: 上传的PDF文件
- `results/`: 转换后的ZIP结果文件
- `temp/`: 临时文件目录

## 与Marker Server集成

本应用需要连接Marker Server进行PDF转换。在Web界面中配置：

1. 打开 http://localhost:5000
2. 在"服务器配置"区域输入Marker Server地址
3. 默认地址：`http://localhost:8001`
4. 点击"测试连接"验证

### 启动Marker Server

如果需要启动Marker Server，可以使用以下命令：

```bash
docker run -d \
  --name markerserver \
  --gpus all \
  -p 8001:8000 \
  registry.cn-shanghai.aliyuncs.com/yangjiacheng1996/marker_server:v1.9.3-cuda129
```

## 健康检查

容器包含健康检查，可通过以下命令查看：

```bash
docker inspect --format='{{.State.Health.Status}}' pdf-converter
```

## 故障排除

### 常见问题

1. **端口冲突**
   - 错误：`Bind for 0.0.0.0:5000 failed: port is already allocated`
   - 解决：修改docker-compose.yml中的端口映射，如`5001:5000`

2. **权限问题**
   - 错误：`Permission denied` when accessing volumes
   - 解决：确保宿主机目录有适当的读写权限

3. **连接Marker Server失败**
   - 错误：`无法连接到Marker Server`
   - 解决：确认Marker Server正在运行且网络可达

4. **容器启动失败**
   - 查看详细日志：`docker logs pdf-converter`
   - 检查依赖：确保requirements.txt中的所有包正确安装

### 日志查看

```bash
# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs pdf-to-markdown-webapp

# 查看Docker容器日志
docker logs -f pdf-converter
```

## 开发模式

如需在开发模式下运行，修改docker-compose.yml：

```yaml
environment:
  - FLASK_ENV=development
```

然后重启服务：
```bash
docker-compose restart
```

## 生产部署建议

1. **使用反向代理**
   - 建议使用Nginx作为反向代理
   - 配置SSL证书启用HTTPS

2. **资源限制**
   - 在docker-compose.yml中设置资源限制
   - 示例：
     ```yaml
     deploy:
       resources:
         limits:
           memory: 512M
           cpus: '1.0'
     ```

3. **监控和日志**
   - 配置日志轮转
   - 使用监控工具（如Prometheus）监控应用状态

## 文件结构

```
.
├── Dockerfile              # Docker构建文件
├── docker-compose.yml      # Docker Compose配置
├── build.sh               # 构建脚本
├── README_DOCKER.md       # Docker部署文档
├── app.py                 # Flask应用
├── start_server.py        # 启动脚本
├── requirements.txt       # Python依赖
├── index.html            # 前端页面
├── style.css             # 样式文件
└── script.js             # 前端逻辑
```

## 技术支持

如有问题，请查看：
- 应用日志：`docker-compose logs`
- Docker状态：`docker-compose ps`
- 系统资源：`docker stats`