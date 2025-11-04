# Mineru Web界面使用说明

## 项目概述

Mineru Web界面是一个基于Flask的Web应用程序，提供友好的用户界面来使用Mineru VLLM Server将PDF文件转换为Markdown格式。

### 主要功能

- ✅ 拖拽上传PDF文件
- ✅ 完整的服务器配置选项
- ✅ 实时转换进度显示
- ✅ 转换结果管理（下载/删除）
- ✅ 重复文件检测和提示
- ✅ 响应式设计，支持移动设备



## 直接运行容器

```bash
docker run -d  --name mineru-web -p 5000:5000 --restart always registry.cn-shanghai.aliyuncs.com/yangjiacheng1996/mineru-vllm-server:web
```

## 手动安装

### 1. 安装依赖

```bash
cd /opt/workspace/pdf2markdown/mineru_client/web
pip install -r requirements.txt
```

### 2. 启动Web服务器

```bash
python app.py
```

服务器将在 `http://127.0.0.1:5000` 启动

### 3. 访问Web界面

在浏览器中打开 `http://127.0.0.1:5000`

## 使用流程

### 第一步：配置服务器

1. **Mineru Server地址**：输入mineru-vllm-server的URL地址
   - 默认值：`http://172.27.213.31:30000`
   - 点击"测试连接"按钮验证服务器是否可达

2. **转换方法**：
   - OCR模式：适合扫描版PDF，使用OCR技术识别文字
   - 文本模式：适合文字版PDF，直接提取文字

3. **表格格式**：
   - Markdown表格：转换为标准的Markdown表格格式
   - HTML表格：保留HTML表格格式

4. **PDF语言**：选择PDF文档的语言，用于提高OCR精度
   - 支持中文、英文、日文、韩文等多种语言
   - 默认"自动检测"

5. **设备模式**：选择计算设备
   - CPU：使用CPU进行计算
   - CUDA：使用GPU加速（需要NVIDIA显卡和CUDA环境）

6. **页面范围**：指定转换的起始和结束页码（从0开始）

7. **公式解析**：启用或禁用数学公式解析

8. **表格解析**：启用或禁用表格解析

### 第二步：上传PDF文件

1. **拖拽上传**：直接将PDF文件拖拽到上传区域
2. **点击选择**：点击"选择文件"按钮选择PDF文件
3. **文件验证**：系统会自动验证文件格式和重复性

### 第三步：开始转换

1. **自动开始**：文件上传后会自动加入转换队列
2. **进度监控**：在进度区域查看实时转换状态
3. **日志查看**：查看详细的转换日志信息

### 第四步：下载结果

1. **结果列表**：转换完成后会在结果区域显示
2. **下载文件**：点击"下载"按钮获取转换结果的zip包
3. **文件管理**：可以删除不需要的转换结果

## 文件结构说明

```
mineru_client/web/
├── app.py                 # Flask后端服务器
├── index.html             # 主页面
├── style.css              # 样式文件
├── script.js              # 前端JavaScript
├── requirements.txt       # Python依赖
├── 使用说明.md            # 本使用说明文档
├── mineru_client.py       # Mineru客户端封装
├── html_table_to_markdown.py # HTML表格转换工具
├── uploads/               # 临时上传文件目录（自动创建）
└── results/               # 转换结果zip文件目录（自动创建）
```

## API接口说明

### 测试服务器连接
- **POST** `/api/server/test`
- 参数：`{"server_url": "http://server:port"}`

### 转换PDF文件
- **POST** `/api/convert`
- 参数：FormData包含文件和各种配置参数

### 获取结果列表
- **GET** `/api/results`

### 下载结果文件
- **GET** `/api/results/<filename>`

### 删除结果文件
- **DELETE** `/api/results/<filename>`

### 健康检查
- **GET** `/api/health`

### 根路由（提供前端页面）
- **GET** `/`

## 技术架构

### 前端技术
- **HTML5**：页面结构
- **CSS3**：样式和动画效果
- **JavaScript**：交互逻辑和API调用
- **响应式设计**：支持各种屏幕尺寸

### 后端技术
- **Flask**：Python Web框架
- **Flask-CORS**：跨域请求支持
- **子进程管理**：调用mineru命令行工具

## 注意事项

### 文件处理
1. **文件重复检测**：如果已存在同名转换结果，会提示用户先删除已有文件
2. **临时文件清理**：转换完成后会自动清理上传的临时文件
3. **文件大小限制**：大文件转换可能需要较长时间

### 服务器要求
1. **Mineru Server**：必须确保mineru-vllm-server正常运行
2. **网络连接**：Web服务器需要能访问mineru-vllm-server
3. **磁盘空间**：确保有足够的磁盘空间存储转换结果

### 转换性能
1. **转换时间**：PDF转换可能需要较长时间，取决于文件大小和复杂度
2. **内存使用**：大文件转换可能需要较多内存
3. **超时设置**：转换过程有60分钟超时限制

## 故障排除

### 常见问题及解决方案

#### 1. 服务器连接失败
- 检查mineru-vllm-server是否启动
- 确认URL地址和端口正确
- 检查防火墙和网络连接

#### 2. 转换失败
- 检查PDF文件是否损坏
- 查看服务器日志获取详细错误信息
- 确认有足够的磁盘空间

#### 3. 下载失败
- 检查文件是否存在于results目录
- 确认文件权限设置正确

#### 4. 页面显示异常
- 清除浏览器缓存
- 检查浏览器控制台是否有JavaScript错误

### 日志查看

服务器运行日志保存在 `server.log` 文件中，可以查看详细的错误信息：

```bash
tail -f server.log
```

## 版本信息

- 版本：1.0
- 作者：RAG项目组
- 更新日期：2025-11-04
- 修复内容：添加根路由解决404错误问题

## 技术支持

如果遇到问题，请：
1. 首先查看本使用说明
2. 检查服务器日志文件
3. 确认mineru-vllm-server正常运行
4. 验证网络连接和文件权限

---
*本使用说明最后更新于2025-11-04*