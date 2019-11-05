# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class ScheduleModel(object):
    @staticmethod
    def get_interface_detail(cursor, dispatch_id):
        """获取工作流预警详情"""
        command = '''
        SELECT a.interface_id, b.interface_name, retry, b.run_time,
        c.config_id AS success_alert, d.config_id AS failed_alert
        FROM tb_dispatch AS a
        LEFT JOIN tb_interface AS b ON a.interface_id = b.interface_id AND b.is_deleted = 0
        LEFT JOIN tb_dispatch_alert AS c ON a.dispatch_id = c.dispatch_id AND c.is_deleted = 0 AND c.alert_type = 1
        LEFT JOIN tb_dispatch_alert AS d ON a.dispatch_id = d.dispatch_id AND d.is_deleted = 0 AND d.alert_type = 2
        WHERE a.dispatch_id = :dispatch_id AND a.`status` != 0
        '''

        result = cursor.query_one(command, {
            'dispatch_id': dispatch_id
        })
        return result if result else {}

    @staticmethod
    def get_run_job_detail(cursor, interface_id):
        """获取运行任务详情"""
        command = '''
        SELECT a.job_id, a.job_name, c.prep_id, b.server_host, a.server_dir, a.server_script, run_period, return_code
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
    def get_prep_job_detail(cursor, job_id):
        """获取依赖任务详情"""
        command = '''
        SELECT a.job_id, b.server_host, a.server_dir, a.server_script, run_period
        FROM tb_jobs AS a
        LEFT JOIN tb_exec_host AS b ON a.server_id = b.server_id AND b.is_deleted = 0
        WHERE a.job_id = :job_id AND a.is_deleted = 0
        '''
        result = cursor.query_one(command, {
            'job_id': job_id
        })
        return result if result else {}

    @staticmethod
    def update_exec_job_status(cursor, exec_id, job_id, status):
        """修改执行任务状态"""
        command = '''
            UPDATE tb_execute_detail
            SET status = :status, update_time = :update_time, pid = 0
            WHERE exec_id = :exec_id AND job_id = :job_id
            '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'job_id': job_id,
            'status': status,
            'update_time': int(time.time())
        })
        return result
