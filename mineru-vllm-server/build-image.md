B站Pansir视频：【地表最强（暂时）PDF OCR工具更新了】 https://www.bilibili.com/video/BV11tHnzgEeG/?share_source=copy_web&vd_source=4cee0005e63af504f1a4e5f79e975468

亲测可用
由于实验过最新版安装，启动时报错，为了避免折腾，直接照搬视频中的成功案例，所有软件版本与视频一致。
所以容器镜像规定为 nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04
这个镜像的python版本是3.12.3
flash_attn版本最高适配：
https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.2/flash_attn-2.8.2+cu12torch2.7cxx11abiFALSE-cp312-cp312-linux_x86_64.whl
https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.2/flash_attn-2.8.2+cu12torch2.7cxx11abiTRUE-cp312-cp312-linux_x86_64.whl
如果pytorch采用pip安装，选择第一个，本文采用第一个。如果pytorch采用源码编译安装并打开了C++的abi功能，则选择第二个。

| 特性 | cxx11abiFALSE 版本 | cxx11abiTRUE 版本 |
| :--- | :--- | :--- |
| **CXX11 ABI 状态** | 编译时未启用较新的 C++11 ABI（_GLIBCXX_USE_CXX11_ABI =0） | 编译时启用了较新的 C++11 ABI（_GLIBCXX_USE_CXX11_ABI =1） |
| **兼容的 PyTorch** | 与 PyTorch 官方预编译包（来自 pip/conda）兼容（官方包默认使用旧 ABI 编译） | 与从源代码自行编译的 PyTorch 兼容（编译时默认启用新 ABI） |
| **适用场景** | 绝大多数用户使用 `pip install torch` 安装的 PyTorch 环境 | 少数用户从源码编译 PyTorch 且未显式禁用新 ABI 的环境 |
| **常见性** | **最常用** | 较少见 |


### 容器构建
先手动构建
```bash
# 启动容器
docker run --name mineru2.5 -it --gpus all nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04 /bin/bash

# 查看显卡驱动
nvidia-smi

# 系统包
apt update && apt upgrade -y
apt install -y vim git python3-pip python3-venv curl net-tools wget
apt install -y libgobject-2.0-0 libpango-1.0-0 libpangoft2-1.0-0 
apt install -y libgl1 libglib2.0-0t64 libsm6 libxext6 libxrender-dev

# 虚拟环境
cd /opt
python3 -m venv venv-mineru2-5
source venv-mineru2-5/bin/activate
python -V
mkdir ~/.pip
vim ~/.pip/pip.conf
------------------------
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

pip install -U pip setuptools wheel

# 安装uv
pip install uv

# 安装cuda对应版本的pytorch
pip install torch==2.7.1+cu128 torchvision==0.22.1+cu128 torchaudio==2.7.1+cu128 --index-url https://download.pytorch.org/whl/cu128

# 安装flash-attn
wget https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.2/flash_attn-2.8.2+cu12torch2.7cxx11abiFALSE-cp312-cp312-linux_x86_64.whl
pip install ./flash_attn-2.8.2+cu12torch2.7cxx11abiFALSE-cp312-cp312-linux_x86_64.whl --extra-index-url https://download.pytorch.org/whl/cu128

# 安装vllm
pip install vllm==0.10.0 --extra-index-url https://download.pytorch.org/whl/cu128

# 安装transformers
pip install -U transformers==4.53.2

# 安装minerU
uv pip install mineru[all] -i https://pypi.tuna.tsinghua.edu.cn/simple

# 下载模型（魔法上网）
export HF_ENDPOINT=https://hf-mirror.com
mineru-vllm-server --port 30000

# 按ctrl+c关闭server。exit退出容器
```
### 构建后端server镜像

```bash
# 将手动构建的容器提交为一个镜像
docker commit mineru2.5 mineru2-5-base

# 编写一个Dockerfile
-------------------------------------
FROM mineru2-5-base

LABEL maintainer="Yang Jiacheng"
LABEL runcommand="docker run -d --name mineru-vllm-server --gpus all -p 30000:30000 mineru-vllm-server:v2.5-cuda128"

SHELL ["/bin/bash", "-c"]
# 启动命令
ENTRYPOINT ["/opt/venv-mineru2-5/bin/mineru-vllm-server"]

CMD ["--port", "30000"]
-------------------------------------

# 构建镜像
docker build . -t mineru-vllm-server:v2.5-cuda128

# 导出
docker save -o mineru-vllm-server-cu128.tar mineru-vllm-server:v2.5-cuda128

# 导入
docker load -i mineru-vllm-server-cu128.tar

# 启动
docker run -d --name mineru-vllm-server --gpus all -p 30000:30000 mineru-vllm-server:v2.5-cuda128
用户使用
# 安装uv
pip install uv 或者 
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
irm https://astral.sh/uv/install.ps1 | iex       # Windows (PowerShell)

# 安装minerU
uv pip install mineru

# 进行pdf转换
mineru -p /path/to/your.pdf  -o /path/to/output/dir  -b vlm-http-client -u http://127.0.0.1:30000 -m ocr

```

### 视频笔记
```bash
python环境准备
conda create -n M-vllm python=3.12 -y
conda activate M-vllm

# 先部署vllm基础环境
pip install -U pip setuptools wheel
pip install -U uv
pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.2/flash_attn-2.8.2+cu12torch2.7cxx11abiFALSE-cp312-cp312-linux_x86_64.whl
pip install vllm==0.10.0 --extra-index-url https://download.pytorch.org/whl/cu128
pip install -U transformers==4.53.2

# 安装minerU 2.5
uv pip install mineru[all]
# 检验mineru版本号
mineru -v

# 启动mineru server
mineru-vllm-server --port 30000
# 首次启动模型会自动下载模型，需要魔法网络，默认从huggingface下载模型。
# 出现Application startup complete. 表示启动成功。

# 客户端
uv pip install mineru

# 文档转换
mineru -p /path/to/your.pdf  -o /path/to/output/dir  -b vlm-http-client -u http://127.0.0.1:30000

确认最新的稳定版flash_attn。访问 https://github.com/Dao-AILab/flash-attention/releases  ，人工确认。
然后直接pip install 最新flash_attn
pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.2/flash_attn-2.8.2+cu12torch2.7
```
