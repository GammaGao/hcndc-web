# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class EventModel(object):
    @staticmethod
    def get_interface_detail_by_ftp_event_id(cursor, ftp_event_id):
        """获取任务流详情by文件事件id"""
        command = '''
        SELECT b.interface_id, c.interface_name, a.date_time
        FROM tb_file_event AS a
        LEFT JOIN tb_file_event_interface AS b USING(ftp_event_id)
        LEFT JOIN tb_interface AS c ON b.interface_id = c.interface_id AND c.is_deleted = 0
        WHERE ftp_event_id = :ftp_event_id AND a.`status` != 0;
        '''
        result = cursor.query(command, {
            'ftp_event_id': ftp_event_id
        })
        return result if result else []

    @staticmethod
    def add_event_execute(cursor, exec_type, event_id, run_date, date_format):
        """添加事件执行表"""
        command = '''
        INSERT INTO tb_event_execute(exec_type, event_id, `status`, run_date, date_format,
        insert_time, update_time)
        VALUES (:exec_type, :event_id, 1, :run_date, :date_format, :insert_time, :update_time)
        '''
        result = cursor.insert(command, {
            'exec_type': exec_type,
            'event_id': event_id,
            'run_date': run_date,
            'date_format': date_format,
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def add_event_exec_interface(cursor, data):
        """添加事件执行任务流依赖表"""
        command = '''
        INSERT INTO tb_event_execute_interface(exec_id, interface_id, in_degree, out_degree, `level`, is_tree,
        `status`, insert_time, update_time)
        VALUES (:exec_id, :interface_id, :in_degree, :out_degree, :level, :is_tree, :status, :insert_time, :update_time)
        '''
        result = cursor.insert(command, args=data)
        return result

    @staticmethod
    def add_event_execute_detail(cursor, data):
        """添加事件执行详情表"""
        command = '''
        INSERT INTO tb_event_execute_detail(exec_id, interface_id, job_id, in_degree, out_degree, params_value,
        server_host, server_dir, server_script, return_code, position, `level`, `status`, insert_time, update_time)
        VALUES (:exec_id, :interface_id, :job_id, :in_degree, :out_degree, :params_value, :server_host, :server_dir,
        :server_script, :return_code, :position, :level, :status, :insert_time, :update_time)
        '''
        result = cursor.insert(command, data)
        return result

    @staticmethod
    def update_file_event_run_time(cursor, ftp_event_id, date_time):
        """修改事件调度账期"""
        command = '''
        UPDATE tb_file_event
        SET date_time = :date_time, update_time = :update_time
        WHERE ftp_event_id = :ftp_event_id
        '''
        result = cursor.update(command, {
            'ftp_event_id': ftp_event_id,
            'date_time': date_time,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def update_event_exec_interface_status(cursor, exec_id, interface_id, status):
        """修改事件执行任务流状态"""
        command = '''
        UPDATE tb_event_execute_interface
        SET status = :status, update_time = :update_time
        WHERE exec_id = :exec_id AND interface_id = :interface_id
        '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'interface_id': interface_id,
            'status': status,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def update_event_exec_job_status(cursor, exec_id, interface_id, job_id, status):
        """修改事件执行任务状态"""
        command = '''
        UPDATE tb_event_execute_detail
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
    def get_event_exec_interface_by_exec_id(cursor, exec_id):
        """获取事件执行任务流依赖表by执行id"""
        command = '''
        SELECT interface_id, in_degree, out_degree, `level`, `status`
        FROM tb_event_execute_interface
        WHERE exec_id = :exec_id AND is_tree = 1
        '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })
        return result if result else []

    @staticmethod
    def update_event_execute_status(cursor, exec_id, status):
        """修改事件调度执行表状态"""
        command = '''
        UPDATE tb_event_execute
        SET status = :status, update_time = :update_time
        WHERE exec_id = :exec_id
        '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'status': status,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def get_event_interface_detail_last_execute(cursor, interface_id):
        """获取事件最后一次执行任务流详情"""
        command = '''
        SELECT a.interface_id, interface_name, retry, b.`status`, c.`status` AS last_status
        FROM tb_interface AS a
        LEFT JOIN tb_event_execute_interface AS b ON a.interface_id = b.interface_id
        LEFT JOIN (
        -- 上一次执行状态
        SELECT a.interface_id, b.`status`
        FROM tb_interface AS a
        LEFT JOIN tb_event_execute_interface AS b ON a.interface_id = b.interface_id
        WHERE a.interface_id = :interface_id AND a.is_deleted = 0
        ORDER BY b.id DESC
        LIMIT 1, 1
        ) AS c ON a.interface_id = c.interface_id
        WHERE a.interface_id = :interface_id AND a.is_deleted = 0
        ORDER BY b.id DESC
        LIMIT 1
        '''
        result = cursor.query_one(command, {
            'interface_id': interface_id
        })
        return result if result else {}

    @staticmethod
    def get_event_execute_jobs(cursor, exec_id, interface_id):
        """获取事件所有执行任务"""
        command = '''
        SELECT job_id, in_degree, out_degree, server_host, server_dir,
        server_script, position, `level`, a.`status`, params_value, return_code
        FROM tb_event_execute_detail AS a
        -- 主表状态为运行中,失败(执行中存在错误),就绪
        INNER JOIN tb_event_execute AS b ON a.exec_id = b.exec_id AND b.`status` IN (1, -1, 3)
        WHERE a.exec_id = :exec_id AND a.interface_id = :interface_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id,
            'interface_id': interface_id
        })
        return result if result else []

    @staticmethod
    def add_event_exec_detail_job(cursor, exec_id, interface_id, job_id, level, server_dir, server_script, message,
                                  type):
        """添加执行任务详情日志"""
        command = '''
        INSERT INTO tb_event_detail_logs(exec_id, interface_id, job_id, `level`,
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

    @staticmethod
    def get_event_exec_detail_success(cursor, event_id, run_date):
        """获取事件id某日期执行成功日志详情"""
        command = '''
        SELECT exec_id, exec_type, event_id, `status`, run_date, date_format
        FROM tb_event_execute
        WHERE STR_TO_DATE(run_date, date_format) = :run_date AND event_id = :event_id AND `status` = 0
        '''
        result = cursor.query_one(command, {
            'run_date': run_date,
            'event_id': event_id
        })
        return result if result else {}
