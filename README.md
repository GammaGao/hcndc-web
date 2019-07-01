* [一、需求分析](#一、需求分析)
    * [1.引言](#1.引言)
        * [1.1 项目背景](#1.1项目背景)
        * [1.2 编写目的](#1.2编写目的)
        * [1.3 需求整理](#1.3需求整理)
            * [1.3.1 kettle执行流程](#1.3.1kettle执行流程)
            * [1.3.2 kettle数据库](#1.3.2kettle数据库)
            * [1.3.3 azkaban数据库](#1.3.3azkaban数据库)
    * [2.需求摘要](#2.需求摘要)
        * [2.1 原型界面](#2.1原型界面)
        * [2.2 数据库设计](#2.2数据库设计)
        * [2.3 环境相关](#2.3环境相关)
        * [2.4 项目层级](#2.4项目层级)
        * [2.5 架构图](#2.5架构图)
* [二、代码详解](#二、代码详解)
* [三、部署运行](#三、部署运行)
*   [1.中间件依赖](#1.中间件依赖)
*   [2.安装python相关依赖包](#2.安装python相关依赖包)
    *   [2.1 调度系统服务端](#2.1调度系统服务端)
    *   [2.2 调度系统执行端](#2.2调度系统执行端)
*   [3.生成mysql配置表](#3.生成mysql配置表)
*   [4.配置mysql用户权限表(数据没存)](#4.配置mysql用户权限表(数据没存))
*   [5.配置调度系统相关配置](#5.配置调度系统相关配置)
*   [6.启动程序](#6.启动程序)
    *   [6.1 服务端](#6.1服务端)
    *   [6.2 执行端](#6.2执行端)

# 网状分布式调度平台——执行端
[HCNDC-exec](https://github.com/laixin86714802/HCNDC-exec.git)

# 一、需求分析
## 1.引言

### 1.1 项目背景
随着etl组同步数据任务的增加，原有架构和流程难以满足当前业务场景。原有架构中，kettle管理调度和执行任务多功能并用，由于kettle软件的局限性，不足以行使调度角色的功能，调度任务时，使用线性模型，并随着调度任务的增多，任务维护和监控工作逐渐繁重，机器资源消耗过多。本项目使用网状模型重构ETL架构，将调度从kettle中分离，参考开源项目[azkaban](https://github.com/azkaban/azkaban)部分流程,使用python重写代码逻辑。

### 1.2 编写目的
本文档用于产品策划与研发，为技术开发人员及测试人员提供规格依据。
### 1.3 需求整理
#### 1.3.1 kettle执行流程
![](/x_other/kettle_flow.jpg)
原有流程以kettle为中心，根据优先级取作业，同接口下任务线性执行。
#### 1.3.2 kettle数据库
![](/x_other/etl_db.png)
主要配置：
任务配置：接口表、调度表、调度前置表等；
kettle配置：数据库配置表、数据传输表、文本配置表等；
**注：该数据库设计调度和执行模块耦合过于紧密**
#### 1.3.3 azkaban数据库
![](/x_other/azkaban_db.png)
主要配置：
调度配置：项目表、执行job表；
触发器配置：触发器表；
执行表：执行流表；
日志表：job执行日志表；
**注：该数据库设计中longblob类型字段过多，直接将字段序列化后存入，设计数据库过于偷懒**

## 2.需求摘要
### 2.1 原型界面
| 页面名称 | URI | 描述 |
| ------------ | ------------ | ------------ |
| 登录 | /login/ | 登入、登出 |
| 接口 | /interface/ | 增改查，详情，列表 |
| 任务 | /job/ | 增改查，详情，列表 |
| 调度 | /dispatch/ | 增改查，详情，列表，执行，暂停，恢复 |
| 调度预警 | /dispatch/alert/ | 增改查，详情，列表 |
| 预警配置 | /base/alert/ | 增改查，列表 |
| 执行服务器 | /base/exec/host/ | 增改查，列表 |
| 执行 | /execute/ | 详情，日志，列表，拓扑 |

8个模块，共20多个页面

### 2.2 数据库设计
![](/x_other/hcdnc_db.png)
主要配置：
用户配置：用户、角色、权限表；
任务配置：接口、任务表；
调度配置：调度、持久化、调度预警表；
执行配置：执行、详情表；

### 2.3 环境相关
系统：Win或Linux
语言：Python 3.6.4
框架：后端-Flask、前端-Echarts、UI-layui

### 2.4 项目层级
```
HCNDC-web
├─conn # 数据库连接类
├─document # 接口文档类
├─filters # 接口过滤类
├─models # 模型类
├─operations # 操作类
├─resources # 接口入口类
├─route # 路由类
├─rpc # rpc客户端
├─scheduler # 调度线程类
├─server # 项目常用类
├─static # 静态资源
│ ├─css
│ ├─echarts
│ ├─fonts
│ ├─images
│ ├─js # 各页面前端事件、渲染
│ │ ├─base
│ │ ├─dispatch
│ │ ├─execute
│ │ ├─interface
│ │ ├─job
│ │ └─util
│ └─layui # UI模块
│ ├─css
│ │ └─modules
│ │ ├─laydate
│ │ │ └─default
│ │ └─layer
│ │ └─default
│ ├─font
│ ├─images
│ │ └─face
│ └─lay
│ └─modules
├─templates # 前端模板
│ ├─base
│ ├─dispatch
│ ├─exception
│ ├─execute
│ ├─interface
│ ├─job
│ └─util
├─util # 基础类
└─verify # 参数过滤类
```
### 2.5 架构图
![](/x_other/framework.png)

# 二、代码详解
关键字，以后写
```
权限模块
矢量图: 深拷贝,浅拷贝
日历插件
api文档
日志过多影响性能 fluentd+mongo
微服务+docker 容器轻量化
权限管理
响应时间500ms
栅格系统
wc -l `find -path ./venv -prune -o -name '*py'`
orm封装
Celery, rpc, kafka 集群服务
azkaban序列化, 反序列化
/home/xuexiang/azkaban-2.5.0/azkaban-executor-2.5.0/executions
ProcessBuilder
apscheduler持久化 防止宕机
WSGI接口
rpc通信 封装tpc协议
show global variables like 'wait_timeout';
SELECT @@wait_timeout;
db.getCollection('scheduler_lock').createIndex({"export": 1}, {expireAfterSeconds: 0})//分布式锁超时索引
```

# 三、部署运行
## 1.中间件依赖
```
fluentd——日志流处理工具
mongdb——日志存储数据库
mysql——配置数据库
python3.6——执行环境
uwsgi——web服务器
```

## 2.安装python相关依赖包
### 2.1 调度系统服务端
cd /HCNDC-web
pip install -r requirements.txt

### 2.2 调度系统执行端
cd /HCNDC-exec
pip install -r requirements.txt

## 3.生成mysql配置表
执行"调度平台数据库ddl.txt"SQL语句

## 4.配置mysql用户权限表(数据没存)


## 5.配置调度系统相关配置
./代码/HCNDC-web/superconf.json
./代码/HCNDC-exec/superconf.json
```
配置主要字段说明：
1.mysql对象：mysql的配置
2.log对象：fluentd日志的配置
3.mongo对象：mongo数据库的配置
4.schedule对象：调度并发数，每个任务最大实例数配置
5.exec对象：执行端的端口，持久化的表名
6.master对象：服务端的IP和端口
```
## 6.启动程序
### 6.1 服务端
cd /HCNDC-web
python server.py
### 6.2 执行端
cd /HCNDC-exec
python server.py
