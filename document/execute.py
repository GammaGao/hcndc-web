# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

# 执行服务回调请求
callback_request = api.doc(params={
    'exec_id': '执行id',
    'status': '任务状态'
})

# 执行列表请求值
execute_list_request = api.doc(params={
    'interface_id': '接口id',
    'start_time': '开始运行时间',
    'end_time': '结束运行时间',
    'run_status': '运行状态: 0.全部, 1.成功, 2.运行中, 3.失败',
    'exec_type': '执行类型: 0.全部, 1.调度, 2.手动',
    'page': '页码',
    'limit': '条数'
})

# 执行日志请求
execute_log_request = api.doc(params={
    'exec_id': '执行id',
    'job_id': '任务id'
})

# 执行拓扑结构请求
execute_graph_request = api.doc(params={
    'exec_id': '执行id'
})