# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class ExecHostModel(object):
    @staticmethod
    def get_exec_host_list(cursor, condition, page, limit):
        """获取执行服务器列表"""
        command = '''
        SELECT server_id, server_host, server_name, is_deleted
        FROM tb_exec_host
        %s
        ORDER BY server_id
        LIMIT :limit OFFSET :offset

        '''
        command = command % condition

        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_exec_host_count(cursor, condition):
        """获取执行服务器条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_exec_host
        %s
        '''

        command = command % condition

        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def get_exec_host_detail(cursor, server_id):
        """获取执行服务器详情"""
        command = '''
        SELECT server_id, server_host, server_name, is_deleted
        FROM tb_exec_host
        WHERE server_id = :server_id
        '''
        result = cursor.query_one(command, {
            'server_id': server_id
        })
        return result if result else {}

    @staticmethod
    def get_exec_host_in_dispatch_job(cursor, server_id):
        """获取调度任务中存在执行服务器个数"""
        command = '''
        SELECT count(*) AS count
        FROM tb_dispatch AS a
        LEFT JOIN tb_interface AS b ON a.interface_id = b.interface_id AND b.is_deleted = 0
        LEFT JOIN tb_jobs AS c ON b.interface_id = c.interface_id AND c.is_deleted = 0
        WHERE a.`status` != 0 AND c.server_id = :server_id
        '''
        result = cursor.query_one(command, {
            'server_id': server_id
        })
        return result['count'] if result else 0

    @staticmethod
    def update_exec_host_detail(cursor, server_id, server_host, server_name, is_deleted, user_id):
        """修改执行服务器详情"""
        command = '''
        UPDATE tb_exec_host
        SET server_host = :server_host, server_name = :server_name,
        update_time = :update_time, updater_id = :user_id, is_deleted = :is_deleted
        WHERE server_id = :server_id
        '''
        result = cursor.update(command, {
            'server_id': server_id,
            'server_host': server_host,
            'server_name': server_name,
            'update_time': int(time.time()),
            'is_deleted': is_deleted,
            'user_id': user_id
        })
        return result

    @staticmethod
    def delete_exec_host_detail(cursor, server_id, user_id):
        """删除执行服务器详情"""
        command = '''
        UPDATE tb_exec_host
        SET update_time = :update_time, updater_id = :user_id, is_deleted = 1
        WHERE server_id = :server_id
        '''
        result = cursor.delete(command, {
            'update_time': int(time.time()),
            'user_id': user_id,
            'server_id': server_id
        })
        return result

    @staticmethod
    def add_exec_host_detail(cursor, server_host, server_name, user_id):
        """新增执行服务器"""
        command = '''
        INSERT INTO tb_exec_host(server_host, server_name, insert_time, update_time, creator_id, updater_id)
        VALUES(:server_host, :server_name, :insert_time, :update_time, :user_id, :user_id)
        '''
        result = cursor.insert(command, {
            'server_host': server_host,
            'server_name': server_name,
            'insert_time': int(time.time()),
            'update_time': int(time.time()),
            'user_id': user_id
        })
        return result

    @staticmethod
    def get_exec_host_all(cursor):
        """获取所有执行服务器"""
        command = '''
        SELECT server_id, server_host
        FROM tb_exec_host
        WHERE is_deleted = 0
        '''
        result = cursor.query(command)
        return result if result else []

    @staticmethod
    def get_exec_host_status(cursor, condition, page, limit):
        """获取执行服务器状态"""
        command = '''
        SELECT server_id, server_host, server_name, core_num, system_version, disk_used,
        disk_all, memory_used, memory_all, last_ping_time, process_status
        FROM tb_exec_host AS a
        LEFT JOIN tb_exec_host_status AS b USING(server_id)
        WHERE is_deleted = 0 %s
        LIMIT :limit OFFSET :offset
        '''
        command = command % condition
        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_exec_host_status_count(cursor, condition):
        """获取执行服务器状态条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_exec_host AS a
        LEFT JOIN tb_exec_host_status AS b USING(server_id)
        WHERE is_deleted = 0 %s
        '''
        command = command % condition
        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def get_exec_host_status_by_host(cursor, server_host):
        """根据域名获取服务器状态"""
        command = '''
        SELECT server_id, b.id AS status_id
        FROM tb_exec_host
        LEFT JOIN tb_exec_host_status AS b USING(server_id)
        WHERE server_host = :server_host
        '''
        result = cursor.query_one(command, {
            'server_host': server_host
        })
        return result if result else {}

    @staticmethod
    def update_exec_host_status_by_host_success(cursor, server_id, core_num, system_version, disk_used,
                                                disk_all, memory_used, memory_all, last_ping_time, process_status):
        """根据域名更新服务器状态-成功时"""
        command = '''
        UPDATE tb_exec_host_status
        SET core_num = :core_num, system_version = :system_version, disk_used = :disk_used, disk_all = :disk_all,
        memory_used = :memory_used, memory_all = :memory_all, last_ping_time = :last_ping_time, process_status = :process_status
        WHERE server_id = :server_id
        '''
        result = cursor.update(command, {
            'server_id': server_id,
            'core_num': core_num,
            'system_version': system_version,
            'disk_used': disk_used,
            'disk_all': disk_all,
            'memory_used': memory_used,
            'memory_all': memory_all,
            'last_ping_time': last_ping_time,
            'process_status': process_status
        })
        return result

    @staticmethod
    def add_exec_host_status_by_host_success(cursor, server_id, core_num, system_version, disk_used,
                                             disk_all, memory_used, memory_all, last_ping_time, process_status):
        """根据域名新增服务器状态-成功时"""
        command = '''
        INSERT INTO tb_exec_host_status(server_id, core_num, system_version, disk_used,
        disk_all, memory_used, memory_all, last_ping_time, process_status)
        VALUES(:server_id, :core_num, :system_version, :disk_used,
        :disk_all, :memory_used, :memory_all, :last_ping_time, :process_status)
        '''
        result = cursor.insert(command, {
            'server_id': server_id,
            'core_num': core_num,
            'system_version': system_version,
            'disk_used': disk_used,
            'disk_all': disk_all,
            'memory_used': memory_used,
            'memory_all': memory_all,
            'last_ping_time': last_ping_time,
            'process_status': process_status
        })
        return result

    @staticmethod
    def update_exec_host_status_by_host_failed(cursor, server_id, last_ping_time, process_status):
        """根据域名更新服务器状态-失败时"""
        command = '''
        UPDATE tb_exec_host_status
        SET last_ping_time = :last_ping_time, process_status = :process_status
        WHERE server_id = :server_id
        '''
        result = cursor.update(command, {
            'server_id': server_id,
            'last_ping_time': last_ping_time,
            'process_status': process_status
        })
        return result

    @staticmethod
    def add_exec_host_status_by_host_failed(cursor, server_id, last_ping_time, process_status):
        """"根据域名新增服务器状态-失败时"""
        command = '''
        INSERT INTO tb_exec_host_status(server_id, last_ping_time, process_status)
        VALUES (:server_id, :last_ping_time, :process_status)
        '''
        result = cursor.insert(command, {
            'server_id': server_id,
            'last_ping_time': last_ping_time,
            'process_status': process_status
        })
        return result


class AlertModel(object):
    @staticmethod
    def get_alert_conf_list(cursor, condition, page, limit):
        """获取预警配置列表"""
        command = '''
        SELECT id, alert_channel, conf_name, param_host, param_port, param_config, is_deleted
        FROM tb_dispatch_alert_conf
        %s
        ORDER BY id
        LIMIT :limit OFFSET :offset
        '''

        command = command % condition

        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_alert_conf_count(cursor, condition):
        """获取预警配置条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_dispatch_alert_conf
        %s
        '''
        command = command % condition

        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def get_alert_conf_list_all(cursor):
        """获取预警配置列表(全)"""
        command = '''
        SELECT id, alert_channel, conf_name, param_config
        FROM tb_dispatch_alert_conf
        WHERE is_deleted = 0
        '''
        result = cursor.query(command)
        return result if result else []

    @staticmethod
    def get_alert_in_dispatch(cursor, conf_id):
        """获取预警配置在调度中个数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_dispatch AS a
        LEFT JOIN tb_dispatch_alert AS b ON a.dispatch_id = b.dispatch_id AND b.is_deleted = 0
        LEFT JOIN tb_dispatch_alert_conf AS c ON b.config_id = c.id AND c.is_deleted = 0
        WHERE a.`status` != 0 AND c.id = :conf_id
        '''
        result = cursor.query_one(command, {
            'conf_id': conf_id
        })
        return result['count'] if result else 0

    @staticmethod
    def delete_alert_config(cursor, conf_id, user_id):
        """删除预警配置"""
        command = '''
        UPDATE tb_dispatch_alert_conf
        SET is_deleted = 1, update_time = :update_time, updater_id = :user_id
        WHERE id = :conf_id
        '''
        result = cursor.delete(command, {
            'update_time': int(time.time()),
            'conf_id': conf_id,
            'user_id': user_id
        })
        return result

    @staticmethod
    def get_alert_config_detail(cursor, conf_id):
        """获取预警配置详情"""
        command = '''
        SELECT id, alert_channel, conf_name, param_host, param_port, param_config, param_pass, is_deleted
        FROM tb_dispatch_alert_conf
        WHERE id = :conf_id
        '''
        result = cursor.query_one(command, {
            'conf_id': conf_id
        })
        return result if result else {}

    @staticmethod
    def update_alert_config_detail(cursor, conf_id, alert_channel, conf_name, param_config, param_host, param_port,
                                   param_pass, is_deleted, user_id):
        """修改预警配置详情"""
        command = '''
        UPDATE tb_dispatch_alert_conf
        SET alert_channel = :alert_channel, conf_name = :conf_name, param_host = :param_host,
        param_port = :param_port, param_config = :param_config,
        param_pass = :param_pass, update_time = :update_time, updater_id = :user_id, is_deleted = :is_deleted
        WHERE id = :conf_id
        '''
        result = cursor.update(command, {
            'conf_id': conf_id,
            'alert_channel': alert_channel,
            'conf_name': conf_name,
            'param_config': param_config,
            'param_host': param_host,
            'param_port': param_port,
            'param_pass': param_pass,
            'update_time': int(time.time()),
            'is_deleted': is_deleted,
            'user_id': user_id
        })
        return result

    @staticmethod
    def add_alert_config_detail(cursor, alert_channel, conf_name, param_config, param_host, param_port, param_pass,
                                user_id):
        """新增预警配置"""
        command = '''
        INSERT INTO tb_dispatch_alert_conf(alert_channel, conf_name, param_config, param_host, param_port, param_pass,
        insert_time, update_time, creator_id, updater_id)
        VALUES(:alert_channel, :conf_name, :param_config, :param_host, :param_port, :param_pass,
        :insert_time, :update_time, :user_id, :user_id)
        '''
        result = cursor.insert(command, {
            'alert_channel': alert_channel,
            'conf_name': conf_name,
            'param_config': param_config,
            'param_host': param_host,
            'param_port': param_port,
            'param_pass': param_pass,
            'insert_time': int(time.time()),
            'update_time': int(time.time()),
            'user_id': user_id
        })
        return result
