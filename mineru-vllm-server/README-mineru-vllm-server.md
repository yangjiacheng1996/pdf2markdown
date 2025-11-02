# 部署和使用后端
```
docker pull registry.cn-shanghai.aliyuncs.com/yangjiacheng1996/mineru-vllm-server:v2.5-cuda128
docker run -d --name mineru-vllm-server --gpus all -p 30000:30000 mineru-vllm-server:v2.5-cuda128
使用：
uv pip install mineru
mineru -p /path/to/your.pdf  -o /path/to/output/dir  -b vlm-http-client -u http://127.0.0.1:30000 -m ocr
```