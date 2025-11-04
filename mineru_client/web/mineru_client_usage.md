# Mineru客户端使用说明

## 概述

`mineru_client.py` 是一个集成脚本，将mineru命令和HTML表格转换功能结合，实现PDF到Markdown的一键转换，支持表格格式转换。

## 功能特性

- ✅ 一键PDF到Markdown转换
- ✅ 支持HTML表格和Markdown表格格式
- ✅ 自动检测虚拟环境中的mineru命令
- ✅ 完整的错误处理和日志输出
- ✅ 支持多种OCR语言和配置选项
- ✅ 支持页面范围选择和公式解析

## 安装要求

1. 确保已安装Python 3.7+
2. 确保已安装mineru命令（在.venv虚拟环境中）
3. 确保`html_table_to_markdown.py`在同一目录下

## 使用方法

### 基本用法

```bash
# 使用OCR模式，默认转换为Markdown表格
python mineru_client.py -p document.pdf -o ./output -u http://172.27.213.31:30000
```

### 高级用法

```bash
# 使用文本模式，保留HTML表格格式
python mineru_client.py -p doc.pdf -o ./md -u http://localhost:30000 -m text -t html

# 指定语言和页面范围
python mineru_client.py -p doc.pdf -o ./output -u http://172.27.213.31:30000 -l ch -s 0 -e 10

# 禁用公式解析
python mineru_client.py -p doc.pdf -o ./output -u http://172.27.213.31:30000 -f False
```

## 参数说明

### 必需参数

- `-p, --pdf-path`: PDF文件路径
- `-o, --output-dir`: Markdown输出目录
- `-u, --url`: mineru-vllm-server的URL

### 可选参数

- `-m, --method`: 转换方法，`txt`（文本模式）或`ocr`（OCR模式），默认: `ocr`
- `-t, --table-format`: 表格格式，`html`或`markdown`，默认: `markdown`
- `-l, --lang`: PDF语言，用于提高OCR精度
- `-s, --start-page`: 起始页码（从0开始）
- `-e, --end-page`: 结束页码（从0开始）
- `-f, --formula`: 启用公式解析，True/False
- `--table`: 启用表格解析，True/False
- `-d, --device`: 设备模式，如`cpu`, `cuda`, `cuda:0`等

## 语言支持

支持以下语言选项：
- `ch`: 中文
- `ch_server`: 中文服务器版
- `ch_lite`: 中文轻量版
- `en`: 英文
- `korean`: 韩文
- `japan`: 日文
- `chinese_cht`: 繁体中文
- 以及其他多种语言

## 环境配置

### 虚拟环境设置

确保在虚拟环境中运行，mineru命令已安装：

```bash
# 激活虚拟环境
.\.venv\Scripts\activate

# 检查mineru是否可用
mineru --version
```

### 服务器配置

确保mineru-vllm-server正在运行，URL格式为：`http://IP地址:端口`

## 错误处理

脚本包含完整的错误处理机制：

1. **mineru命令检查**: 自动检测mineru是否可用
2. **文件存在检查**: 验证PDF文件是否存在
3. **目录创建**: 自动创建输出目录
4. **超时处理**: mineru命令60分钟超时保护
5. **表格转换错误**: 表格转换失败时不影响整体流程

## 输出文件

转换完成后，Markdown文件将保存在指定的输出目录中，文件名与PDF文件同名（扩展名为.md）。

## 故障排除

### mineru命令不可用

```bash
错误: mineru命令不可用，请确保已安装并在PATH中或虚拟环境中
```

**解决方案**:
- 确保在虚拟环境中运行
- 检查mineru是否正确安装：`mineru --version`

### PDF文件不存在

```bash
错误: PDF文件不存在: /path/to/document.pdf
```

**解决方案**:
- 检查PDF文件路径是否正确
- 确保文件扩展名为.pdf

### 表格转换失败

```bash
表格转换失败: [错误信息]
```

**解决方案**:
- 检查`html_table_to_markdown.py`是否存在
- 确保有足够的权限写入输出文件

## 性能优化建议

1. **大文件处理**: 对于大型PDF文件，建议使用页面范围参数分段处理
2. **OCR模式**: 对于扫描版PDF，使用OCR模式（`-m ocr`）
3. **文本模式**: 对于文字版PDF，使用文本模式（`-m txt`）以获得更好的性能
4. **硬件加速**: 如有GPU，使用`-d cuda`参数加速处理

## 版本信息

- 版本: 1.0
- 作者: RAG项目组
- 更新日期: 2025-11-03