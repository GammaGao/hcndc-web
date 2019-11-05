# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 任务列表请求值
job_list_request = api.doc(params={
    'job_name': '项目名称',
    'start_time': '开始创建时间',
    'end_time': '结束创建时间',
    'interface_id': '工作流id',
    'is_deleted': '是否使用: 0全部, 1使用, 2失效',
    'page': '页码',
    'limit': '条数'
})

# 任务列表返回值
job_list_response_success = api.response(200, '成功', api.model('job_list_response_success', {
    'state': fields.Integer(description=200),
    'msg': fields.String(description='成功'),
    'data': fields.Nested(model=api.model('job_list_response_data', {
        'job_id': fields.String(description='任务id'),
        'user_name': fields.String(description='创建者'),
        'job_name': fields.String(description='任务名称'),
        'description': fields.String(description='任务描述'),
        'server_host': fields.String(description='服务器域名'),
        'server_user': fields.String(description='服务器用户'),
        'server_dir': fields.String(description='服务器目录'),
        'server_script': fields.String(description='脚本命令'),
        'is_deleted': fields.Integer(description='是否失效'),
        'retry': fields.Integer(description='重试次数'),
        'update_time': fields.String(description='修改时间')
    }), description='任务列表返回值')
}))

# 任务修改请求
job_update_request = api.doc(body=api.model('job_update_request', {
    'job_name': fields.String(description='任务名称'),
    'interface_id': fields.Integer(description='工作流id'),
    'job_desc': fields.String(description='任务描述'),
    'server_id': fields.String(description='执行服务器id'),
    'server_dir': fields.String(description='服务器目录'),
    'server_script': fields.String(description='脚本命令'),
    'return_code': fields.Integer(description='返回状态码:自定义的进程状态码'),
    'old_prep': fields.String(description='原依赖任务'),
    'job_prep': fields.String(description='依赖任务'),
    'old_params': fields.String(description='原任务参数'),
    'job_params': fields.String(description='任务参数'),
    'is_deleted': fields.Integer(description='是否删除: 0否, 1是')
}, description='任务修改请求参数'))

# 任务新增请求
job_add_request = api.doc(body=api.model('job_add_request', {
    'job_name': fields.String(description='任务名称'),
    'interface_id': fields.Integer(description='工作流id'),
    'job_desc': fields.String(description='任务描述'),
    'server_id': fields.Integer(description='执行服务器id'),
    'server_dir': fields.String(description='服务器目录'),
    'server_script': fields.String(description='脚本命令'),
    'job_prep': fields.String(description='依赖任务'),
    'job_params': fields.String(description='任务参数'),
    'return_code': fields.Integer(description='返回状态码:自定义的进程状态码')
}, description='任务新增请求参数'))

# 获取所有任务请求
all_job_request = api.doc(params={
    'interface_id': '工作流id'
})

# 立即执行任务请求
job_execute_request = api.doc(body=api.model('job_execute_request', {
    'job_id': fields.Integer(description='任务id')
}, description='立即执行任务请求'))
