# PDF转Markdown Web应用

基于Marker Server的PDF转Markdown Web界面，提供拖拽上传、进度显示和结果管理功能。

## 功能特性

- 🚀 **拖拽上传** - 支持拖拽PDF文件到上传区域
- ⚙️ **服务器配置** - 可配置远程Marker Server地址和端口
- 📊 **实时进度** - 显示转换进度和详细日志
- 📦 **自动打包** - 将Markdown文件和图片打包为ZIP文件
- 📱 **响应式设计** - 适配桌面和移动设备
- 🗑️ **文件管理** - 支持下载和删除转换结果
- ⚠️ **重复检测** - 检测同名文件避免重复转换

## 文件结构

```
marker_client/
├── index.html          # 主页面
├── style.css           # 样式文件
├── script.js           # 前端逻辑
├── app.py              # 后端服务器
├── start_server.py     # 启动脚本
├── requirements.txt    # Python依赖
└── README.md           # 说明文档
```

## 安装和运行

### 前提条件

1. 已安装Python 3.7+
2. 已安装Marker Server并运行在某个端口（如8001），如果您没有安装Server，需要在支持cuda12.9的显卡服务器上运行一下命令：
    ```
    docker run -d --name markerserver --gpus all -p 8000:8000 registry.cn-shanghai.aliyuncs.com/yangjiacheng1996/marker_server:v1.9.3-cuda129  
    ```
3. 部署client的服务器网络可访问Marker Server

### 快速启动

1. **安装依赖**
   ```bash
   cd parser/demo
   pip install -r requirements.txt
   ```

2. **启动Web应用**
   ```bash
   # 方式1：使用启动脚本
   python start_server.py
   
   # 方式2：直接运行
   python app.py
   ```

3. **访问应用**
   打开浏览器访问: http://localhost:5000

### 配置Marker Server

在Web界面中配置Marker Server地址：
- 默认地址: `http://localhost:8001`
- 支持远程服务器地址

## 使用说明

### 1. 配置服务器
- 在"服务器配置"区域输入Marker Server地址
- 点击"测试连接"验证服务器是否可用
- 选择转换选项（强制OCR、输出格式等）

### 2. 上传文件
- **拖拽上传**: 将PDF文件拖拽到虚线区域
- **点击上传**: 点击"选择文件"按钮选择PDF文件
- 支持多文件上传，自动排队处理

### 3. 监控进度
- 在"转换进度"区域查看实时进度
- 查看详细日志了解转换状态
- 进度条显示整体转换进度

### 4. 管理结果
- 在"转换结果"区域查看所有转换完成的ZIP文件
- 点击"下载"按钮下载ZIP文件到本地
- 点击"删除"按钮删除不需要的结果文件

## API接口

### 测试服务器连接
```http
POST /api/server/test
Content-Type: application/json

{
  "server_url": "http://localhost:8001"
}
```

### 转换PDF文件
```http
POST /api/convert
Content-Type: multipart/form-data

参数:
- file: PDF文件
- server_url: Marker Server地址
- force_ocr: 是否强制OCR
- output_format: 输出格式 (markdown/json/html)
- page_range: 页面范围
```

### 获取结果列表
```http
GET /api/results
```

### 下载结果文件
```http
GET /api/results/{filename}
```

### 删除结果文件
```http
DELETE /api/results/{filename}
```

## 技术实现

### 前端技术
- **HTML5** - 页面结构
- **CSS3** - 响应式样式和动画
- **JavaScript** - 交互逻辑和API调用
- **Fetch API** - 异步请求处理

### 后端技术
- **Flask** - Web框架
- **Flask-CORS** - 跨域支持
- **Requests** - HTTP客户端
- **Zipfile** - ZIP文件处理

### 主要特性
1. **文件上传**: 支持拖拽和点击上传
2. **进度跟踪**: 实时显示转换进度和日志
3. **错误处理**: 完善的错误提示和重试机制
4. **文件管理**: 自动清理临时文件，管理结果文件
5. **并发安全**: 支持多文件排队处理

## 故障排除

### 常见问题

1. **无法连接到Marker Server**
   - 检查Marker Server是否运行
   - 确认端口和地址正确
   - 检查防火墙设置

2. **文件上传失败**
   - 检查文件是否为PDF格式
   - 确认文件大小在合理范围内
   - 检查网络连接

3. **转换过程卡住**
   - 检查Marker Server日志
   - 确认PDF文件没有损坏
   - 尝试重启Web应用

4. **无法下载结果**
   - 检查results目录权限
   - 确认ZIP文件已生成
   - 检查浏览器下载设置

### 日志查看

Web应用会在控制台输出详细日志，包括：
- 服务器连接状态
- 文件上传进度
- 转换过程状态
- 错误信息

## 开发说明

### 自定义配置

修改 `app.py` 中的配置项：
```python
UPLOAD_FOLDER = 'uploads'      # 上传文件目录
RESULTS_FOLDER = 'results'     # 结果文件目录
TEMP_FOLDER = 'temp'           # 临时文件目录
```

### 扩展功能

可以扩展的功能：
- 添加用户认证
- 支持更多文件格式
- 添加批量处理
- 集成云存储
- 添加转换历史

## 许可证

本项目基于MIT许可证开源。

## 支持

如有问题或建议，请提交Issue或联系开发团队。

# 附录
本文还提供了一个marker_client脚本，用于在命令行中将本地文档转换为markdown文件。无需安装和打开浏览器。
```bash
python marker_client.py  -s http://localhost:8000  -p /path/to/your/helloworld.pdf  -o /path/to/your/output/folder/

# see more options
python marker_client.py --help
```
