### 启动Marker Server

如果需要启动Marker Server，可以使用以下命令：

```bash
docker run -d \
  --name markerserver \
  --gpus all \
  -p 8001:8000 \
  registry.cn-shanghai.aliyuncs.com/yangjiacheng1996/marker_server:v1.9.3-cuda129
```

# 镜像构建笔记
基本容器环境
```
# 启动容器
docker run --name marker -it --gpus all nvidia/cuda:12.9.1-cudnn-devel-ubuntu24.04 /bin/bash


# 查看显卡驱动
nvidia-smi


# 系统包
apt update && apt upgrade -y
apt install -y vim git python3-pip python3-venv curl net-tools
apt install -y libgobject-2.0-0 libpango-1.0-0 libpangoft2-1.0-0 


# 虚拟环境
cd /opt
python3 -m venv venv-marker
source venv-marker/bin/activate
python -V
mkdir ~/.pip
vim ~/.pip/pip.conf
------------------------
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn


pip install -U pip setuptools wheel




# 安装cuda对应版本的pytorch
pip install torch==2.8.0+cu129 torchvision==0.23.0+cu129 torchaudio==2.8.0+cu129 --index-url https://download.pytorch.org/whl/cu129


# 安装全量marker
pip install marker-pdf[full]
pip install streamlit streamlit-ace psutil
pip install -U uvicorn fastapi python-multipart


# 模型下载
自己新建一个helloworld.pdf，内容就是一句话Hello world! 然后执行如下命令下载模型
# 容器外将pdf文件传入容器内
docker cp ./helloworld.pdf  marker:/opt
# 容器内执行转换命令下载模型
marker_single /opt/helloworld.pdf --output_dir /opt


# 使用marker命令行
marker_single --help
marker_single /path/to/file.pdf


# web页面
marker_gui


# 后端
marker_server --port 8000

```


容器变镜像
```
# 将容器导出为tar
docker export -o marker_container.tar marker


# 导入容器
docker import marker_container.tar marker:cuda129


# 将容器提交为镜像
docker commit marker marker:cuda129


# 基于镜像二创
-------------------------------------
FROM marker:cuda129

# 维护者信息
LABEL maintainer="Yang Jiacheng"
LABEL runcommand="docker run -d --name markerserver --gpus all -p 8000:8000 marker_server:v1.9.3-cuda129"

SHELL ["/bin/bash", "-c"]

# 启动命令
ENTRYPOINT ["/opt/venv-marker/bin/marker_server"]
CMD ["--port", "8000", "--host", "0.0.0.0"]
-------------------------------------------


# 构建
docker build . -t marker_server:v1.9.3-cuda129


# 导出镜像
docker save -o markerserver_cuda129.tar markerserver:cuda129


# 导入镜像
docker load -i markerserver_cuda129.tar


# 启动二创镜像
docker run -d --name markerserver --gpus all -p 8000:8000 marker_server:v1.9.3-cuda129


docker run -d --name markerserver --gpus '"device=4"' -p 8000:8000 markerserver:cuda128 --port 8000 --host 0.0.0.0 

```










