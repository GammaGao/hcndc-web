# !/usr/bin/env python
# -*- coding: utf-8 -*-

class ExecuteModel(object):
    @staticmethod
    def add_execute(cursor, exec_type, dispatch_id):
        """添加执行表"""
        command = '''
        INSERT INTO tb_execute(exec_type, dispatch_id, `status`, insert_time, update_time)
        VALUES(:exec_type, :dispatch_id, 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP())
        '''
        result = cursor.insert(command, {
            'exec_type': exec_type,
            'dispatch_id': dispatch_id
        })
        return result

    @staticmethod
    def update_execute_datetime(cursor, exec_id, status):
        """修改调度执行表时间"""
        command = '''
        UPDATE tb_execute
        SET status = :status, update_time = UNIX_TIMESTAMP()
        WHERE exec_id = :exec_id
        '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'status': status
        })
        return result

    @staticmethod
    def get_execute_detail_status(cursor, exec_id):
        """获取执行详情任务状态"""
        command = '''
        SELECT `status`
        FROM tb_execute_detail
        WHERE exec_id = :exec_id AND position = 1
        '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })
        return [i['status'] for i in result] if result else []

    @staticmethod
    def add_execute_detail(cursor, data):
        """添加执行详情表"""
        command = '''
        INSERT INTO tb_execute_detail(exec_id, job_id, in_degree, out_degree,
        server_host, server_dir, server_script, position, `level`, `status`, insert_time, update_time)
        VALUES (:exec_id, :job_id, :in_degree, :out_degree, :server_host, :server_dir, :server_script,
        :position, :level, :status, UNIX_TIMESTAMP(), UNIX_TIMESTAMP())
        '''
        result = cursor.insert(command, data)
        return result

    @staticmethod
    def get_execute_jobs(cursor, exec_id):
        """获取所有执行任务"""
        command = '''
        SELECT job_id, in_degree, out_degree, server_host, server_dir, server_script, position, `level`, `status`
        FROM tb_execute_detail
        WHERE exec_id = :exec_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })
        return result if result else []

    @staticmethod
    def get_execute_list(cursor, condition, page=1, limit=10):
        """获取执行列表"""
        command = '''
        SELECT exec_id, interface_id, dispatch_name, dispatch_desc, exec_type, a.`status`,
        a.insert_time, a.update_time, a.update_time - a.insert_time AS timedelta
        FROM tb_execute AS a
        LEFT JOIN tb_dispatch AS b USING(dispatch_id)
        %s
        ORDER BY exec_id DESC
        LIMIT :limit OFFSET :offset
        '''

        command = command % condition

        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_execute_count(cursor, condition):
        """获取执行列表条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_execute AS a
        LEFT JOIN tb_dispatch AS b USING(dispatch_id)
        %s
        '''

        command = command % condition

        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def get_execute_detail(cursor, exec_id):
        """获取执行详情"""
        command = '''
        SELECT a.id, job_id, server_host, server_dir, server_script, position, a.`status`,
        a.insert_time, a.update_time, a.update_time - a.insert_time AS timedelta,
        (a.insert_time - b.insert_time) / (b.update_time - b.insert_time) AS margin_left,
        (a.update_time - a.insert_time) / (b.update_time - b.insert_time) AS width
        FROM tb_execute_detail AS a
        LEFT JOIN tb_execute AS b USING(exec_id)
        WHERE exec_id = :exec_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })
        return result if result else []

    @staticmethod
    def get_execute_log_by_job(cursor, exec_id, job_id):
        """获取任务执行日志"""
        result = [i for i in cursor.find(
            {'exec_id': exec_id, 'job_id': job_id},
            {'level', 'message', 'time'}
        ).sort([('_id', 1)])]
        return result

    @staticmethod
    def get_execute_log(cursor, exec_id):
        """获取执行日志"""
        result = [i for i in cursor.find(
            {'exec_id': exec_id},
            {'level', 'message', 'time'}
        ).sort([('_id', 1)])]
        return result

    @staticmethod
    def get_execute_graph(cursor, exec_id):
        """获取执行拓扑结构"""
        command = '''
        SELECT interface_id, job_id, job_name, in_degree, out_degree, `level`, `status`
        FROM tb_execute_detail AS a
        LEFT JOIN tb_jobs AS b USING(job_id)
        WHERE exec_id = :exec_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })

        return result if result else []

    @staticmethod
    def get_execute_alert(cursor, exec_id, alert_type):
        """获取执行预警"""
        command = '''
        SELECT a.exec_id, a.dispatch_id, d.dispatch_name, alert_channel, param_host, param_port,
        param_config, param_pass, b.send_mail, a.update_time, a.is_push
        FROM tb_execute AS a
        LEFT JOIN tb_dispatch_alert AS b ON a.dispatch_id = b.dispatch_id AND b.alert_type = :alert_type AND b.is_deleted = 0
        LEFT JOIN tb_dispatch_alert_conf AS c ON b.config_id = c.id AND c.is_deleted = 0
        LEFT JOIN tb_dispatch AS d ON a.dispatch_id = d.dispatch_id
        WHERE a.exec_id = :exec_id
        '''

        result = cursor.query_one(command, {
            'exec_id': exec_id,
            'alert_type': alert_type
        })
        return result if result else {}

    @staticmethod
    def update_msg_push(cursor, exec_id):
        """修改消息推送状态"""
        command = '''
        UPDATE tb_execute
        SET is_push = 1, update_time = UNIX_TIMESTAMP()
        WHERE exec_id = :exec_id
        '''
        result = cursor.update(command, {
            'exec_id': exec_id
        })
        return result
