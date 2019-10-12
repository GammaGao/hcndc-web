# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import api
from flask_restplus import fields

# 获取执行服务器请求
exec_host_request = api.doc(params={
    'server_name': '服务器名称',
    'server_host': '服务器IP',
    'is_deleted': '是否删除: 0全部, 1正常, 2删除',
    'page': '页码',
    'limit': '条数'
})

# 执行服务器修改请求
exec_host_update_request = api.doc(body=api.model('exec_host_update_request', {
    'server_id': fields.Integer(description='执行服务器id'),
    'server_host': fields.String(description='执行服务器ip'),
    'server_name': fields.String(description='执行服务器名称'),
    'is_deleted': fields.Integer(description='是否失效: 0正常, 1失效')
}, description='执行服务器修改请求'))

# 预警配置列表请求值
alert_conf_list_request = api.doc(params={
    'alert_channel': '预警渠道:0.全部,1.邮件,2.钉钉',
    'conf_name': '配置名称',
    'is_deleted': '是否删除: 0全部, 1正常, 2删除',
    'page': '页码',
    'limit': '条数'
})

# 预警配置列表返回值
alert_conf_list_response_success = api.response(200, '成功', api.model('alert_conf_list_response_success', {
    'state': fields.Integer(description=200),
    'msg': fields.String(description='成功'),
    'data': fields.Nested(model=api.model('alert_conf_list_response_data', {
        'id': fields.String(description='配置id'),
        'alert_channel': fields.String(description='预警渠道:1.邮件,2.钉钉'),
        'conf_name': fields.String(description='配置名称'),
        'param_config': fields.String(description='邮箱/api: 1.邮件: 发件人邮箱, 2.顶顶: 钉钉机器人api')
    }), description='预警配置列表返回值')
}))

# 预警配置详情返回值
alert_conf_detail_response_success = api.response(200, '成功', api.model('alert_conf_detail_response_success', {
    'state': fields.Integer(description=200),
    'msg': fields.String(description='成功'),
    'data': fields.Nested(model=api.model('job_list_response_data', {
        'id': fields.Integer(description='预警配置id'),
        'alert_channel': fields.String(description='预警渠道:1.邮件,2.钉钉'),
        'conf_name': fields.String(description='配置名称'),
        'param_host': fields.String(description='邮箱域名'),
        'param_config': fields.String(description='邮箱/api: 1.邮件: 发件人邮箱, 2.顶顶: 钉钉机器人api'),
        'param_pass': fields.String(description='发件人邮箱密码'),
        'is_deleted': fields.Integer(description='是否失效: 0.正常,1.删除')
    }), description='任务列表返回值')
}))

# 预警配置修改请求
alert_conf_detail_update_request = api.doc(body=api.model('alert_conf_detail_update_request', {
    'alert_channel': fields.Integer(description='预警渠道:1.邮件,2.钉钉'),
    'conf_name': fields.Integer(description='配置名称'),
    'param_config': fields.String(description='邮箱/api: 1.邮件: 发件人邮箱, 2.顶顶: 钉钉机器人api'),
    'param_host': fields.String(description='邮箱域名: eg: smtp.exmail.qq.com'),
    'param_port': fields.Integer(description='邮箱端口: eg: 465'),
    'param_pass': fields.String(description='发件人邮箱密码'),
    'is_deleted': fields.Integer(description='是否失效: 0正常, 1失效')
}, description='执行服务器修改请求'))

# 预警配置新增请求
alert_conf_detail_add_request = api.doc(body=api.model('alert_conf_detail_add_request', {
    'alert_channel': fields.Integer(description='预警渠道:1.邮件,2.钉钉'),
    'conf_name': fields.Integer(description='配置名称'),
    'param_config': fields.String(description='邮箱/api: 1.邮件: 发件人邮箱, 2.顶顶: 钉钉机器人api'),
    'param_host': fields.String(description='邮箱域名: eg: smtp.exmail.qq.com'),
    'param_port': fields.String(description='邮箱端口: eg: 465'),
    'param_pass': fields.String(description='发件人邮箱密码')
}, description='执行服务器修改请求'))

# 测试执行服务器
exec_host_test_request = api.doc(body=api.model('exec_host_test_request', {
    'server_host': fields.String(description='执行服务器ip')
}), description='测试执行服务器')

# 新增执行服务器
exec_host_add_request = api.doc(body=api.model('exec_host_add_request', {
    'server_host': fields.String(description='执行服务器ip'),
    'server_name': fields.String(description='执行服务器名称'),
}), description='新增执行服务器')

# 获取执行服务器状态列表
exec_host_status_list_request = api.doc(params={
    'server_name': '服务器名称',
    'server_host': '服务器IP',
    'page': '页码',
    'limit': '条数'
})
