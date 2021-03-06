# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class ScheduleModel(object):
    # @staticmethod
    # def get_interface_detail(cursor, interface_id):
    #     """获取任务流预警详情"""
    #     command = '''
    #     SELECT a.interface_id, b.interface_name, retry, b.run_time,
    #     c.config_id AS success_alert, d.config_id AS failed_alert
    #     FROM tb_dispatch AS a
    #     LEFT JOIN tb_interface AS b ON a.interface_id = b.interface_id AND b.is_deleted = 0
    #     LEFT JOIN tb_dispatch_alert AS c ON a.dispatch_id = c.dispatch_id AND c.is_deleted = 0 AND c.alert_type = 1
    #     LEFT JOIN tb_dispatch_alert AS d ON a.dispatch_id = d.dispatch_id AND d.is_deleted = 0 AND d.alert_type = 2
    #     WHERE a.dispatch_id = :dispatch_id AND a.`status` != 0
    #     '''
    #
    #     result = cursor.query_one(command, {
    #         'dispatch_id': dispatch_id
    #     })
    #     return result if result else {}

    @staticmethod
    def get_run_job_detail(cursor, interface_id):
        """获取运行任务详情"""
        command = '''
        SELECT a.job_id, a.job_name, c.prep_id, b.server_host, a.server_dir, a.server_script, return_code
        FROM tb_jobs AS a
        LEFT JOIN tb_exec_host AS b ON a.server_id = b.server_id AND b.is_deleted = 0
        -- 依赖作业
        LEFT JOIN (
        SELECT job_id, GROUP_CONCAT(prep_id) AS prep_id
        FROM tb_job_prep
        WHERE is_deleted = 0
        GROUP BY job_id
        ) AS c ON a.job_id = c.job_id
        WHERE a.interface_id = :interface_id AND a.is_deleted = 0
        '''

        result = cursor.query(command, {
            'interface_id': interface_id
        })
        return result if result else []

    @staticmethod
    def get_run_job_detail_by_id(cursor, job_id):
        """获取运行任务详情by任务id"""
        command = '''
        SELECT a.job_id, a.job_name, c.prep_id, b.server_host, a.server_dir, a.server_script, return_code
        FROM tb_jobs AS a
        LEFT JOIN tb_exec_host AS b ON a.server_id = b.server_id AND b.is_deleted = 0
        -- 依赖作业
        LEFT JOIN (
        SELECT job_id, GROUP_CONCAT(prep_id) AS prep_id
        FROM tb_job_prep
        WHERE is_deleted = 0 AND job_id = :job_id
        GROUP BY job_id
        ) AS c ON a.job_id = c.job_id
        WHERE a.job_id = :job_id AND a.is_deleted = 0
        '''
        result = cursor.query_one(command, {
            'job_id': job_id
        })
        return result if result else {}

    @staticmethod
    def update_exec_job_status(cursor, exec_id, interface_id, job_id, status):
        """修改执行任务状态"""
        command = '''
        UPDATE tb_execute_detail
        SET status = :status, update_time = :update_time, pid = 0
        WHERE exec_id = :exec_id AND interface_id = :interface_id AND job_id = :job_id
        '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'interface_id': interface_id,
            'job_id': job_id,
            'status': status,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def update_exec_job_reset(cursor, exec_id, interface_id, job_id, status, job):
        """断点重跑时修改执行任务"""
        command = '''
        UPDATE tb_execute_detail
        SET server_dir = :server_dir, server_script = :server_script, in_degree = :in_degree,
        out_degree = :out_degree, return_code = :return_code, `status` = :status, `level` = :level,
        server_host = :server_host, params_value = :params_value, update_time = :update_time, pid = 0
        WHERE exec_id = :exec_id AND interface_id = :interface_id AND job_id = :job_id
        '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'interface_id': interface_id,
            'job_id': job_id,
            'status': status,
            'level': job['level'],
            'server_dir': job['server_dir'],
            'server_script': job['server_script'],
            'in_degree': ','.join(str(i) for i in job['in']) if job['in'] else '',
            'out_degree': ','.join(str(i) for i in job['out']) if job['out'] else '',
            'return_code': job['return_code'],
            'server_host': job['server_host'],
            'params_value': ','.join(job['params_value']) if job['params_value'] else '',
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def update_exec_interface_reset(cursor, exec_id, interface_id, status, interface):
        """断点重跑时修改执行任务流"""
        command = '''
        UPDATE tb_execute_interface
        SET in_degree = :in_degree, out_degree = :out_degree, `status` = :status,
        `level` = :level, update_time = :update_time
        WHERE exec_id = :exec_id AND interface_id = :interface_id
        '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'interface_id': interface_id,
            'status': status,
            'in_degree': ','.join(str(i) for i in interface['in']) if interface['in'] else '',
            'out_degree': ','.join(str(i) for i in interface['out']) if interface['out'] else '',
            'level': interface['level'],
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def update_exec_job_status_all(cursor, exec_id, status):
        """修改执行任务状态"""
        command = '''
        UPDATE tb_execute_detail
        SET status = :status, update_time = :update_time, pid = 0
        WHERE exec_id = :exec_id
        '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'status': status,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def add_exec_detail_job(cursor, exec_id, interface_id, job_id, level, server_dir, server_script, message, type):
        """添加执行任务详情日志"""
        command = '''
        INSERT INTO tb_schedule_detail_logs(exec_id, interface_id, job_id, `level`,
        server_dir, server_script, `message`, `type`, insert_time)
        VALUES (:exec_id, :interface_id, :job_id, :level, :server_dir, :server_script, :message, :type, :insert_time)
        '''
        result = cursor.insert(command, {
            'exec_id': exec_id,
            'interface_id': interface_id,
            'job_id': job_id,
            'level': level,
            'server_dir': server_dir,
            'server_script': server_script,
            'message': message,
            'type': type,
            'insert_time': int(time.time())
        })
        return result
