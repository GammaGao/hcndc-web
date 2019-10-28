# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class DispatchModel(object):
    @staticmethod
    def add_dispatch_detail(cursor, interface_id, dispatch_name, dispatch_desc, minute, hour, day, month, week,
                            user_id):
        """新增调度"""
        command = '''
        INSERT INTO tb_dispatch(interface_id, dispatch_name, dispatch_desc, `minute`,
        `hour`, `day`, `month`, `week`, creator_id, updater_id, insert_time, update_time, `status`)
        VALUES (:interface_id, :dispatch_name, :dispatch_desc, :minute, :hour,
        :day, :month, :week, :user_id, :user_id, :insert_time, :update_time, 1)
        '''

        result = cursor.insert(command, {
            'interface_id': interface_id,
            'dispatch_name': dispatch_name,
            'dispatch_desc': dispatch_desc,
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'week': week,
            'user_id': user_id,
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def get_dispatch_list(cursor, condition, page, limit):
        """获取调度列表"""
        command = '''
        SELECT dispatch_id, interface_id, dispatch_name, dispatch_desc, `minute`,
        `hour`, `day`, `month`, `week`, `status`, b.next_run_time
        FROM tb_dispatch AS a
        LEFT JOIN tb_scheduler AS b ON CONCAT('scheduler_', a.dispatch_id) = b.id
        %s
        ORDER BY dispatch_id
        LIMIT :limit OFFSET :offset
        '''
        command = command % condition
        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_dispatch_count(cursor, condition):
        """获取调度列表数量"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_dispatch
        %s
        '''
        command = command % condition
        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def get_dispatch_detail(cursor, dispatch_id):
        """获取调度详情"""
        command = '''
        SELECT dispatch_id, interface_id, dispatch_name, dispatch_desc, `minute`,
        `hour`, `day`, `month`, `week`, `status`
        FROM tb_dispatch
        WHERE dispatch_id = :dispatch_id
        '''
        result = cursor.query_one(command, {
            'dispatch_id': dispatch_id
        })
        return result if result else {}

    @staticmethod
    def update_dispatch_detail(cursor, dispatch_id, interface_id, dispatch_name, dispatch_desc, minute, hour, day,
                               month, week, new_status, user_id):
        """修改调度详情"""
        command = '''
        UPDATE tb_dispatch
        SET interface_id = :interface_id, dispatch_name = :dispatch_name,
        dispatch_desc = :dispatch_desc, `minute` = :minute, `hour` = :hour,
        `day` = :day, `month` = :month, `week` = :week, updater_id = :user_id,
        update_time = :update_time, status = :new_status
        WHERE dispatch_id = :dispatch_id
        '''

        result = cursor.update(command, {
            'dispatch_id': dispatch_id,
            'interface_id': interface_id,
            'dispatch_name': dispatch_name,
            'dispatch_desc': dispatch_desc,
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'week': week,
            'user_id': user_id,
            'update_time': int(time.time()),
            'new_status': new_status
        })
        return result

    @staticmethod
    def update_dispatch_status(cursor, dispatch_id, status, user_id):
        """修改/暂停调度任务"""
        command = '''
        UPDATE tb_dispatch
        SET `status` = :status, updater_id = :user_id, update_time = :update_time
        WHERE dispatch_id = :dispatch_id
        '''

        result = cursor.update(command, {
            'dispatch_id': dispatch_id,
            'status': status,
            'user_id': user_id,
            'update_time': int(time.time())
        })
        return result


class DispatchAlertModel(object):
    @staticmethod
    def add_dispatch_alert(cursor, data):
        """新增调度预警(批处理)"""
        command = '''
        INSERT INTO tb_dispatch_alert(dispatch_id, config_id, alert_type, send_mail,
        creator_id, updater_id, insert_time, update_time)
        VALUES(:dispatch_id, :config_id, :alert_type, :send_mail,
        :user_id, :user_id, :insert_time, :update_time)
        '''
        result = cursor.insert(command, args=data)
        return result

    @staticmethod
    def get_dispatch_alert_detail(cursor, dispatch_id):
        """获取调度预警详情"""
        command = '''
        SELECT a.id, dispatch_id, config_id, alert_type, b.alert_channel, a.send_mail, a.is_deleted
        FROM tb_dispatch_alert AS a
        LEFT JOIN tb_dispatch_alert_conf AS b ON a.config_id = b.id
        WHERE dispatch_id = :dispatch_id
        '''
        result = cursor.query(command, {
            'dispatch_id': dispatch_id
        })
        return result if result else []

    @staticmethod
    def update_dispatch_alert_detail(cursor, data):
        """修改调度预警详情"""
        command = '''
        UPDATE tb_dispatch_alert
        SET config_id = :config_id, alert_type = :alert_type, send_mail = :send_mail,
        updater_id = :user_id, update_time = :update_time, is_deleted = :is_deleted
        WHERE id = :id
        '''
        result = cursor.update(command, args=data)
        return result
