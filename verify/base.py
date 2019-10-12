# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class ExecHostVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_exec_host_list(server_name, server_host, is_deleted, page, limit):
        """获取执行服务器列表"""
        if is_deleted < 0 or is_deleted > 2:
            abort(400, **make_result(status=400, msg='是否删除参数错误'))
        return Response(server_name=server_name, server_host=server_host, is_deleted=is_deleted,
                        page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_get_exec_host_detail(server_id):
        """获取执行服务器详情"""
        if not server_id:
            abort(400, **make_result(status=400, msg='执行服务器id不存在'))
        return Response(server_id=server_id)

    @staticmethod
    @make_decorator
    def verify_update_exec_host_detail(server_id, server_host, server_name, is_deleted, user_id):
        """修改执行服务器详情"""
        if not server_id:
            abort(400, **make_result(status=400, msg='执行服务器id不存在'))
        if not server_host:
            abort(400, **make_result(status=400, msg='执行服务器ip不存在'))
        if not server_name:
            abort(400, **make_result(status=400, msg='执行服务器名称不存在'))
        if is_deleted < 0 or is_deleted > 1:
            abort(400, **make_result(status=400, msg='是否删除参数错误'))
        return Response(server_id=server_id, server_host=server_host, server_name=server_name, is_deleted=is_deleted,
                        user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_delete_exec_host_detail(server_id, user_id):
        """删除执行服务器详情"""
        if not server_id:
            abort(400, **make_result(status=400, msg='执行服务器id不存在'))
        return Response(server_id=server_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_test_exec_host(server_host, user_id):
        """测试执行服务器"""
        if not server_host:
            abort(400, **make_result(status=400, msg='执行服务器ip不存在'))
        return Response(server_host=server_host)

    @staticmethod
    @make_decorator
    def verify_add_exec_host(server_host, server_name, user_id):
        """新增执行服务器"""
        if not server_host:
            abort(400, **make_result(status=400, msg='执行服务器ip不存在'))
        if not server_name:
            abort(400, **make_result(status=400, msg='执行服务器名称不存在'))
        return Response(server_host=server_host, server_name=server_name, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_get_exec_host_status(server_host, server_name, page, limit):
        """获取执行服务器状态"""
        return Response(server_host=server_host, server_name=server_name, page=page, limit=limit)


class AlertVerify(object):
    @staticmethod
    @make_decorator
    def verify_get_alert_conf_list(alert_channel, conf_name, is_deleted, page, limit):
        """获取预警配置列表"""
        if alert_channel < 0 or alert_channel > 2:
            abort(400, **make_result(status=400, msg='预警渠道参数错误'))
        if is_deleted < 0 or is_deleted > 2:
            abort(400, **make_result(status=400, msg='是否删除参数错误'))

        return Response(alert_channel=alert_channel, conf_name=conf_name, is_deleted=is_deleted, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_delete_alert_conf(conf_id, user_id):
        """删除预警配置"""
        if not conf_id:
            abort(400, **make_result(status=400, msg='预警配置id不存在'))
        return Response(conf_id=conf_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_get_alert_conf_detail(conf_id):
        """获取预警配置"""
        if not conf_id:
            abort(400, **make_result(status=400, msg='预警配置id不存在'))
        return Response(conf_id=conf_id)

    @staticmethod
    @make_decorator
    def verify_update_alert_conf_detail(conf_id, alert_channel, conf_name, param_config, param_host, param_port,
                                        param_pass, is_deleted, user_id):
        """修改预警配置"""
        if not conf_id:
            abort(400, **make_result(status=400, msg='预警配置id不存在'))
        if alert_channel < 1 or alert_channel > 2:
            abort(400, **make_result(status=400, msg='预警渠道参数错误'))
        if not conf_name:
            abort(400, **make_result(status=400, msg='配置名称参数错误'))
        if not param_config:
            abort(400, **make_result(status=400, msg='参数配置不得为空'))
        return Response(conf_id=conf_id, alert_channel=alert_channel, conf_name=conf_name, param_config=param_config,
                        param_host=param_host, param_port=param_port, param_pass=param_pass, is_deleted=is_deleted,
                        user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_add_alert_conf(alert_channel, conf_name, param_config, param_host, param_port, param_pass, user_id):
        """新增预警配置"""
        if alert_channel < 1 or alert_channel > 2:
            abort(400, **make_result(status=400, msg='预警渠道参数错误'))
        if not conf_name:
            abort(400, **make_result(status=400, msg='配置名称参数错误'))
        if not param_config:
            abort(400, **make_result(status=400, msg='参数配置不得为空'))
        return Response(alert_channel=alert_channel, conf_name=conf_name, param_config=param_config,
                        param_host=param_host, param_port=param_port, param_pass=param_pass, user_id=user_id)
