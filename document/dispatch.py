# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api
from flask_restplus import fields

# cron运行次数
cron_request = api.doc(params={
    'sched': 'cron表达式',
    'timeFormat': '时间格式',
    'queryTimes': '运行次数'
})

# 调度新增请求
dispatch_add_request = api.doc(body=api.model('dispatch_add_request', {
    'interface_id': fields.Integer(description='工作流id'),
    'dispatch_name': fields.String(description='调度名称'),
    'dispatch_desc': fields.String(description='调度描述'),
    'minute': fields.String(description='分: 0-59'),
    'hour': fields.String(description='时: 0-23'),
    'day': fields.String(description='日: 1-31'),
    'month': fields.String(description='月: 1-12'),
    'week': fields.String(description='周: mon-sun')
}, description='调度新增请求参数'))

# 调度预警新增请求
dispatch_alert_add_request = api.doc(body=api.model('dispatch_alert_add_request', {
    'dispatch_id': fields.Integer(description='调度id'),
    'alert_s': fields.Integer(description='执行流成功开关: 0.关闭,1.开启'),
    'alert_f': fields.Integer(description='执行流失败开关: 0.关闭,1.开启'),
    'conf_id_s': fields.Integer(description='配置id(成功): tb_dispatch_alert_conf.id'),
    'conf_id_f': fields.Integer(description='配置id(失败): tb_dispatch_alert_conf.id'),
    'send_mail_s': fields.String(description='发送邮箱(成功)'),
    'send_mail_f': fields.String(description='发送邮箱(失败)')
}, description='调度预警新增请求参数'))

# 调度列表请求
dispatch_list_request = api.doc(params={
    'interface_id': '工作流id',
    'dispatch_name': '调度名称',
    'status': '调度状态:0全部,1删除,2运行中,3暂停',
    'page': '页码',
    'limit': '条数'
})

# 调度修改请求
dispatch_update_request = api.doc(body=api.model('dispatch_update_request', {
    'dispatch_id': fields.Integer(description='调度id'),
    'interface_id': fields.Integer(description='工作流id'),
    'dispatch_name': fields.String(description='调度名称'),
    'dispatch_desc': fields.String(description='调度描述'),
    'minute': fields.String(description='分: 0-59'),
    'hour': fields.String(description='时: 0-23'),
    'day': fields.String(description='日: 1-31'),
    'month': fields.String(description='月: 1-12'),
    'week': fields.String(description='周: mon-sun'),
    'old_status': fields.Integer(description='旧调度状态: 0.删除1.运行中,2.暂停'),
    'new_status': fields.Integer(description='新调度状态: 0.删除1.运行中,2.暂停')
}, description='调度修改请求参数'))

# 立即执行调度请求
dispatch_run_request = api.doc(body=api.model('dispatch_run_request', {
    'dispatch_id': fields.Integer(description='调度id')
}, description='立即执行调度请求'))

# 调度预警修改请求
dispatch_alert_update_request = api.doc(body=api.model('dispatch_alert_update_request', {
    'flow_id': fields.Integer(description='执行流id'),
    'alert_s': fields.Integer(description='执行流成功开关: 0.关闭,1.开启'),
    'alert_f': fields.Integer(description='执行流失败开关: 0.关闭,1.开启'),
    'alert_id_s': fields.Integer(description='预警id(成功), 没有为-1'),
    'alert_id_f': fields.Integer(description='预警id(失败), 没有为-1'),
    'conf_id_s': fields.Integer(description='配置id(成功): tb_dispatch_alert_conf.id'),
    'conf_id_f': fields.Integer(description='配置id(失败): tb_dispatch_alert_conf.id'),
    'send_mail_s': fields.String(description='发送邮箱(成功)'),
    'send_mail_f': fields.String(description='发送邮箱(失败)')
}, description='任务广播修改请求参数'))

# 调度任务暂停/恢复请求参数
dispatch_action_request = api.doc(body=api.model('dispatch_action_request', {
    'action': fields.Integer(description='1.暂停, 2.恢复')
}, description='调度任务暂停/恢复请求参数'))