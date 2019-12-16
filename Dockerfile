# 镜像基础
FROM 172.16.218.11:5000/python:3.6-stretch
MAINTAINER xuexiang feidai.com
#ENV GUNICORN_WORKERS=4
# 工作目录
#COPY ./ /src/
WORKDIR /app
# 添加当前依赖文件到容器
ADD requirements.txt /app
# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo '$TZ' > /etc/timezone
# 安装项目依赖
RUN pip install thrift_sasl==0.2.1 --no-deps -i http://172.16.218.11:8081/repository/pypi-proxy/simple --trusted-host 172.16.218.11
RUN pip install -r requirements.txt -i http://172.16.218.11:8081/repository/pypi-proxy/simple --trusted-host 172.16.218.11
# 配置启动命令
ENTRYPOINT ["python", "server.py"]

# docker build -t hcndc-web .

# docker run -d \
# --name hcndc-web \
# --restart always \
# -p 2333:2333  \
# --network=host \
# 项目文件挂载
# -v /opt/docker/hcndc-web:/app \
# -v /etc/localtime:/etc:ro \
# hcndc-web
