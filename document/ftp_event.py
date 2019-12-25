# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api

from flask_restplus import fields

# 文件事件列表请求值
ftp_event_list_request = api.doc(params={
    'event_name': '文件事件名称',
    'status': '调度状态:0全部, 1失效, 2运行中, 3暂停',
    'page': '页码',
    'limit': '条数'
})

# 文件事件修改请求值
ftp_event_update_request = api.doc(body=api.model('ftp_event_update_request', {
    'ftp_event_id': fields.Integer(description='文件事件id'),
    'event_name': fields.String(description='事件名称'),
    'event_desc': fields.String(description='事件描述'),
    'ftp_id': fields.Integer(description='FTP配置id'),
    'data_path': fields.String(description='文件路径'),
    'file_name': fields.String(description='文件名称'),
    'interface_id': fields.String(description='任务流id列表'),
    'start_time': fields.String(description='开始时间: 默认00:00'),
    'end_time': fields.String(description='结束时间: 默认23:59'),
    'interval_value': fields.Integer(description='间隔值: 单位(分钟)'),
    'old_status': fields.Integer(description='旧调度状态: 0.失效, 1.运行中, 2.暂停'),
    'new_status': fields.Integer(description='新调度状态: 0.失效, 1.运行中, 2.暂停')
}, description='调度修改请求参数'))

# 文件事件新增请求值
ftp_event_add_request = api.doc(body=api.model('ftp_event_add_request', {
    'event_name': fields.String(description='事件名称'),
    'event_desc': fields.String(description='事件描述'),
    'ftp_id': fields.Integer(description='FTP配置id'),
    'data_path': fields.String(description='文件路径'),
    'file_name': fields.String(description='文件名称'),
    'interface_id': fields.String(description='任务流id列表'),
    'start_time': fields.String(description='开始时间: 默认00:00'),
    'end_time': fields.String(description='结束时间: 默认23:59'),
    'interval_value': fields.Integer(description='间隔值: 单位(分钟)'),
}, description='调度修改请求参数'))