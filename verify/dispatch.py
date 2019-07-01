# !/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort

from server.decorators import make_decorator, Response
from server.status import make_result


class DispatchVerify(object):
    @staticmethod
    @make_decorator
    def verify_add_dispatch(interface_id, dispatch_name, dispatch_desc, minute, hour, day, month, week, user_id):
        """新增调度"""
        if not interface_id:
            abort(400, **make_result(status=400, msg='接口id不存在'))
        if not dispatch_name:
            abort(400, **make_result(status=400, msg='调度名称不存在'))
        if not user_id:
            abort(400, **make_result(status=400, msg='用户不存在'))
        return Response(interface_id=interface_id, dispatch_name=dispatch_name, dispatch_desc=dispatch_desc,
                        minute=minute, hour=hour, day=day, month=month, week=week, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_get_dispatch_list(interface_id, dispatch_name, status, page, limit):
        """获取调度列表"""
        if status < 0 or status > 3:
            abort(400, **make_result(status=400, msg='调度状态参数错误'))
        return Response(interface_id=interface_id, dispatch_name=dispatch_name, status=status, page=page, limit=limit)

    @staticmethod
    @make_decorator
    def verify_get_dispatch_detail(dispatch_id):
        """获取调度详情"""
        if not dispatch_id:
            abort(400, **make_result(status=400, msg='调度id不存在'))
        return Response(dispatch_id=dispatch_id)

    @staticmethod
    @make_decorator
    def verify_delete_dispatch_detail(dispatch_id, user_id):
        """删除调度详情"""
        if not dispatch_id:
            abort(400, **make_result(status=400, msg='调度id不存在'))
        return Response(dispatch_id=dispatch_id, user_id=user_id)

    @staticmethod
    @make_decorator
    def verify_update_dispatch_detail(dispatch_id, interface_id, dispatch_name, dispatch_desc, minute, hour, day, month,
                                      week, user_id, old_status, new_status):
        """修改调度详情"""
        if not dispatch_id:
            abort(400, **make_result(status=400, msg='调度id不存在'))
        if not interface_id:
            abort(400, **make_result(status=400, msg='接口id不存在'))
        if not dispatch_name:
            abort(400, **make_result(status=400, msg='调度名称不存在'))
        if not user_id:
            abort(400, **make_result(status=400, msg='用户不存在'))
        if old_status < 0 or old_status > 2:
            abort(400, **make_result(status=400, msg='是否删除参数错误(旧)'))
        if new_status < 0 or new_status > 2:
            abort(400, **make_result(status=400, msg='是否删除参数错误(新)'))
        return Response(dispatch_id=dispatch_id, interface_id=interface_id, dispatch_name=dispatch_name, minute=minute,
                        dispatch_desc=dispatch_desc, hour=hour, day=day, month=month, week=week, user_id=user_id,
                        old_status=old_status, new_status=new_status)

    @staticmethod
    @make_decorator
    def verify_run_dispatch(dispatch_id):
        """立即执行调度任务"""
        if not dispatch_id:
            abort(400, **make_result(status=400, msg='调度id不存在'))
        return Response(dispatch_id=dispatch_id)

    @staticmethod
    @make_decorator
    def verify_action_dispatch(dispatch_id, action, user_id):
        """暂停/恢复调度任务"""
        if not dispatch_id:
            abort(400, **make_result(status=400, msg='调度id不存在'))
        if action < 1 or action > 2:
            abort(400, **make_result(status=400, msg='请求参数错误'))
        return Response(dispatch_id=dispatch_id, action=action, user_id=user_id)


class DispatchAlertVerify(object):
    @staticmethod
    @make_decorator
    def verify_add_dispatch_alert(dispatch_id, alert_s, alert_f, conf_id_s, conf_id_f, user_id, send_mail_s, send_mail_f):
        """新增调度预警"""
        if not dispatch_id:
            abort(400, **make_result(status=400, msg='调度id不得为空'))
        if not alert_s and not alert_f:
            abort(400, **make_result(status=400, msg='请勿保存空配置'))
        if alert_s and not conf_id_s:
            abort(400, **make_result(status=400, msg='预警配置(成功), 配置参数不得为空'))
        if alert_f and not conf_id_f:
            abort(400, **make_result(status=400, msg='预警配置(失败), 配置参数不得为空'))
        return Response(
            dispatch_id=dispatch_id,
            alert_s=alert_s,
            alert_f=alert_f,
            conf_id_s=conf_id_s,
            conf_id_f=conf_id_f,
            user_id=user_id,
            send_mail_s=send_mail_s,
            send_mail_f=send_mail_f
        )

    @staticmethod
    @make_decorator
    def verify_get_dispatch_alert_detail(dispatch_id):
        """获取调度预警详情"""
        if not dispatch_id:
            abort(400, **make_result(status=400, msg='调度id不得为空'))
        return Response(dispatch_id=dispatch_id)

    @staticmethod
    @make_decorator
    def verify_update_dispatch_alert_detail(dispatch_id, alert_s, alert_f, alert_id_s, alert_id_f, conf_id_s, conf_id_f,
                                            user_id, send_mail_s, send_mail_f):
        """修改调度预警详情"""
        if not dispatch_id:
            abort(400, **make_result(status=400, msg='调度id不得为空'))
        if alert_s and not conf_id_s:
            abort(400, **make_result(status=400, msg='预警配置(成功), 配置参数不得为空'))
        if alert_f and not conf_id_f:
            abort(400, **make_result(status=400, msg='预警配置(失败), 配置参数不得为空'))
        return Response(
            dispatch_id=dispatch_id,
            alert_s=alert_s,
            alert_f=alert_f,
            alert_id_s=alert_id_s,
            alert_id_f=alert_id_f,
            conf_id_s=conf_id_s,
            conf_id_f=conf_id_f,
            user_id=user_id,
            send_mail_s=send_mail_s,
            send_mail_f=send_mail_f
        )