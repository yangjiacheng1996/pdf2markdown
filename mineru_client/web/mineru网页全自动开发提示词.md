有个pdf转markdown的项目叫mineru。。
这个项目部署后有个mineru-vllm-server命令，执行mineru-vllm-server命令会启动一个web server,提供了一些接口，让用户上传pdf文件并返回markdown文件。
我针对mineru-vllm-server开发了一个脚本mineru_client/mineru_client.py，可以上传本地文件到远程的接口中获得markdown文件和图片。
最简使用命令是python.exe  .\parser\mineru_client.py  -p D:/下载/guzhuan.pdf  -o  D:/下载  -u http://172.27.213.31:30000 。
一些人不满足于使用脚本，而是想要一个web页面来上传文件，
需要我实现一个html，只要配置远端的mineru-vllm-server的URL地址，就能够将本地文件拖拽到网页框中，或者点击按钮上传文件。
网页中包含一些可选项，比如模式、表格形式等等。自行斟酌脚本中哪些参数可以作为html的下拉框供用户选择。
pdf转换markdown的时间很长，可以打印一些日志，或者marker项目转换时的进度条。然后将获得的markdown文件和图片打包成与文件同名的zip包，放在html的同级目录中，点击下载按钮可以下载。
html会显示有哪些转换结果zip文件，每个zip文件右边有下载和删除两个按钮，点击删除按钮会删除html同级目录下的zip文件，点击下载可以将zip文件下载到用户电脑中。
如果用户上传的文件与转换结果中的zip包同名，会提示已经转换过了，不再重复转换。请先删除已有结果再重新转换的提示框。
我之前开过一个同类项目marker_client/index.html，你也可以参考它，
根据以上内容，在mineru_client/web目录中生成我要的html和其他必要文件。请开始编程吧！