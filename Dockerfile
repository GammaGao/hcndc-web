# 镜像基础
FROM python:3.6
# 工作目录
WORKDIR /app
# 添加当前依赖文件到容器
ADD requirements.txt /app
# 安装项目依赖
RUN pip install -r requirements.txt -i http://172.16.218.11:8081/repository/pypi-proxy/simple --trusted-host 172.16.218.11
# 配置启动命令
ENTRYPOINT ["python", "server.py"]


# docker run -d \
# --name hcndc-web \
# --restart always \
# -p 2333:2333  \
# --network=host \
# -v /root/hcdnc/hcndc-web:/app \
# hcndc-web