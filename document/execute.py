# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restplus import fields

from configs import api

# 执行服务回调请求
callback_request = api.doc(params={
    'exec_id': '执行id',
    'status': '任务状态'
})

# 任务流日志请求值
execute_flow_request = api.doc(params={
    'interface_id': '任务流id',
    'interface_index': '任务流目录名称',
    'run_status': '运行状态: 0.全部, 1.成功, 2.运行中, 3.中断, 4.失败, 5.就绪',
    'start_time': '开始运行时间',
    'end_time': '结束运行时间',
    'page': '页码',
    'limit': '条数'
})

# 任务流历史日志请求值
execute_history_request = api.doc(params={
    'dispatch_id': '调度id',
    'start_time': '开始运行时间',
    'end_time': '结束运行时间',
    'run_status': '运行状态: 0.全部, 1.成功, 2.运行中, 3.中断, 4.失败, 5.就绪',
    'page': '页码',
    'limit': '条数'
})

# 手动执行任务日志请求
execute_job_request = api.doc(params={
    'job_id': '任务id',
    'start_time': '开始运行时间',
    'end_time': '结束运行时间',
    'run_status': '运行状态: 0.全部, 1.成功, 2.运行中, 3.中断, 4.失败, 5.就绪',
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
    'exec_id': '执行id',
    'interface_id': '任务流id: 0.全部, 其他:其他任务流内拓扑'
})

# 中止执行任务请求
execute_stop_requests = api.doc(body=api.model('execute_stop_requests', {
    'exec_id': fields.List(fields.Integer, description='执行ID列表'),
}, description='中止执行任务请求'))

# 断点重跑请求
execute_restart_requests = api.doc(body=api.model('execute_restart_requests', {
    'exec_id': fields.List(fields.Integer, description='执行ID列表')
}, description='断点重跑请求参数'))

# 重置执行任务请求
execute_reset_requests = api.doc(body=api.model('execute_reset_requests', {
    'exec_id': fields.List(fields.Integer, description='执行ID列表'),
}, description='重置执行任务请求'))

# 启动执行任务请求
execute_start_requests = api.doc(body=api.model('execute_start_requests', {
    'exec_id': fields.List(fields.Integer, description='执行ID列表'),
}, description='启动执行任务请求'))
