# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class ExecuteModel(object):
    @staticmethod
    def add_execute(cursor, exec_type, dispatch_id, run_date, is_after, date_format):
        """添加执行表"""
        command = '''
        INSERT INTO tb_execute(exec_type, dispatch_id, `status`, run_date, date_format,
        is_after, insert_time, update_time)
        VALUES (:exec_type, :dispatch_id, 1, :run_date, :date_format, :is_after, :insert_time, :update_time)
        '''
        result = cursor.insert(command, {
            'exec_type': exec_type,
            'dispatch_id': dispatch_id,
            'is_after': is_after,
            'run_date': run_date,
            'date_format': date_format,
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def add_execute_by_id(cursor, exec_id, exec_type, dispatch_id, run_date, is_after):
        """添加执行表"""
        command = '''
        INSERT INTO tb_execute(exec_id, exec_type, dispatch_id, `status`, run_date, is_after, insert_time, update_time)
        VALUES (:exec_id, :exec_type, :dispatch_id, 3, :run_date, :is_after, :insert_time, :update_time)
        '''
        result = cursor.insert(command, {
            'exec_id': exec_id,
            'exec_type': exec_type,
            'dispatch_id': dispatch_id,
            'is_after': is_after,
            'run_date': run_date,
            'insert_time': int(time.time()),
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def update_execute_status(cursor, exec_id, status):
        """修改调度执行表状态"""
        command = '''
        UPDATE tb_execute
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
    def update_execute_stop(cursor, exec_id, status):
        """修改调度执行表状态为中断"""
        command = '''
        UPDATE tb_execute
        SET status = :status, update_time = :update_time
        WHERE exec_id = :exec_id AND status = 1
        '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'status': status,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def update_interface_run_time(cursor, interface_id, run_time):
        """修改调度执行表账期"""
        command = '''
        UPDATE tb_interface
        SET run_time = :run_time, update_time = :update_time
        WHERE interface_id = :interface_id
        '''
        result = cursor.update(command, {
            'interface_id': interface_id,
            'run_time': run_time,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def get_execute_detail_status(cursor, interface_id, exec_id):
        """获取执行详情任务状态"""
        command = '''
        SELECT `status`
        FROM tb_execute_detail
        WHERE exec_id = :exec_id AND interface_id = :interface_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id,
            'interface_id': interface_id
        })
        return [i['status'] for i in result] if result else []

    @staticmethod
    def get_execute_interface_status(cursor, exec_id):
        """获取执行任务流状态"""
        command = '''
        SELECT `status`
        FROM tb_execute_interface
        WHERE exec_id = :exec_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })
        return [i['status'] for i in result] if result else []

    @staticmethod
    def get_execute_status(cursor, exec_id):
        """获取执行表任务状态"""
        command = '''
        SELECT `status`
        FROM tb_execute
        WHERE exec_id = :exec_id
        '''
        result = cursor.query_one(command, {
            'exec_id': exec_id
        })
        return result['status'] if result else None

    @staticmethod
    def add_execute_detail(cursor, data):
        """添加执行详情表"""
        command = '''
        INSERT INTO tb_execute_detail(exec_id, interface_id, job_id, in_degree, out_degree, params_value,
        server_host, server_dir, server_script, return_code, position, `level`, `status`, insert_time, update_time)
        VALUES (:exec_id, :interface_id, :job_id, :in_degree, :out_degree, :params_value, :server_host, :server_dir,
        :server_script, :return_code, :position, :level, :status, :insert_time, :update_time)
        '''
        result = cursor.insert(command, data)
        return result

    @staticmethod
    def get_execute_jobs(cursor, exec_id, interface_id):
        """获取所有执行任务"""
        command = '''
        SELECT job_id, in_degree, out_degree, server_host, server_dir,
        server_script, position, `level`, a.`status`, params_value, return_code
        FROM tb_execute_detail AS a
        -- 主表状态为运行中,失败(执行中存在错误),就绪
        INNER JOIN tb_execute AS b ON a.exec_id = b.exec_id AND b.`status` IN (1, -1, 3)
        WHERE a.exec_id = :exec_id AND a.interface_id = :interface_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id,
            'interface_id': interface_id
        })
        return result if result else []

    @staticmethod
    def get_execute_jobs_all(cursor, exec_id, interface_id):
        """获取所有任务详情"""
        command = '''
        SELECT job_id, in_degree, out_degree, server_host, server_dir,
        server_script, position, `level`, a.`status`, params_value, return_code
        FROM tb_execute_detail AS a
        INNER JOIN tb_execute AS b ON a.exec_id = b.exec_id
        WHERE a.exec_id = :exec_id AND interface_id = :interface_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id,
            'interface_id': interface_id
        })
        return result if result else []

    @staticmethod
    def get_execute_flow(cursor, condition, page=1, limit=10):
        """获取任务流最新日志"""
        command = '''
        SELECT a.interface_id, a.interface_name, a.interface_index,
        IF(ISNULL(d.run_date), a.run_time, d.run_date) AS run_date, b.dispatch_id, d.`status`,
        d.insert_time, d.update_time, d.update_time - d.insert_time AS timedelta, d.exec_id, e.is_free
        FROM tb_interface AS a
        LEFT JOIN tb_dispatch AS b ON a.interface_id = b.interface_id
        -- 调度ID对应最新的执行ID
        LEFT JOIN (
        SELECT a.dispatch_id, MAX(exec_id) AS exec_id
        FROM tb_dispatch AS a
        LEFT JOIN tb_execute AS b ON a.dispatch_id = b.dispatch_id
        GROUP BY a.dispatch_id) AS c ON b.dispatch_id = c.dispatch_id
        LEFT JOIN tb_execute AS d ON c.exec_id = d.exec_id
        LEFT JOIN (
        SELECT exec_id, COUNT(*) AS is_free
        FROM tb_execute_interface
        WHERE `status` = 3
        GROUP BY exec_id
        ) AS e ON d.exec_id = e.exec_id
        WHERE a.is_deleted = 0 %s
        -- 自定义排序: 失败, 中断, 就绪, 运行中, 成功, NULL
        ORDER BY FIELD(IF(ISNULL(d.`status`), -999, d.`status`), -1, 2, 3, 1, 0, -999), a.interface_id
        LIMIT :limit OFFSET :offset
        '''

        command = command % condition

        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_execute_flow_count(cursor, condition):
        """获取任务流最新日志条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_interface AS a
        LEFT JOIN tb_dispatch AS b ON a.interface_id = b.interface_id
        -- 调度ID对应最新的执行ID
        LEFT JOIN (
        SELECT a.dispatch_id, MAX(exec_id) AS exec_id
        FROM tb_dispatch AS a
        LEFT JOIN tb_execute AS b ON a.dispatch_id = b.dispatch_id
        GROUP BY a.dispatch_id) AS c ON b.dispatch_id = c.dispatch_id
        LEFT JOIN tb_execute AS d ON c.exec_id = d.exec_id
        WHERE a.is_deleted = 0 %s
        '''

        command = command % condition

        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def get_execute_flow_history(cursor, dispatch_id, condition, page=1, limit=10):
        """获取任务流历史日志"""
        command = '''
        SELECT a.exec_id, dispatch_name, dispatch_desc, a.exec_type, a.`status`,
        a.insert_time, a.update_time, a.update_time - a.insert_time AS timedelta, a.run_date
        FROM tb_execute AS a
        LEFT JOIN tb_dispatch AS b USING(dispatch_id)
        WHERE b.dispatch_id = :dispatch_id %s
        ORDER BY exec_id DESC
        LIMIT :limit OFFSET :offset
        '''

        command = command % condition

        result = cursor.query(command, {
            'dispatch_id': dispatch_id,
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_execute_flow_history_count(cursor, dispatch_id, condition):
        """获取任务流历史日志条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_execute AS a
        LEFT JOIN tb_dispatch AS b USING(dispatch_id)
        WHERE b.dispatch_id = :dispatch_id %s
        '''

        command = command % condition

        result = cursor.query_one(command, {
            'dispatch_id': dispatch_id
        })
        return result['count'] if result else 0

    @staticmethod
    def get_execute_job_log(cursor, condition, page, limit):
        """获取手动执行任务日志"""
        command = '''
        SELECT a.job_id, a.job_name, a.job_index, c.exec_type, c.insert_time, c.update_time,
        c.update_time - c.insert_time AS timedelta, d.server_host, a.server_dir, a.server_script,
        e.`status`, b.exec_id
        FROM tb_jobs AS a
        -- 任务ID对应最新的执行ID
        LEFT JOIN (
        SELECT a.job_id, MAX(a.exec_id) AS exec_id
        FROM tb_execute_detail AS a
        GROUP BY job_id
        ) AS b USING(job_id)
        LEFT JOIN tb_execute AS c USING(exec_id)
        LEFT JOIN tb_exec_host AS d USING(server_id)
        LEFT JOIN tb_execute_detail AS e ON b.exec_id = e.exec_id AND b.job_id = e.job_id
        %s
        -- 自定义排序: 失败, 等待依赖任务完成, 待运行, 运行中, 成功, NULL
        ORDER BY FIELD(IF(ISNULL(e.`status`), 'null', e.`status`), 'failed', 'ready', 'preparing', 'running', 'succeeded', 'null'), a.job_id
        LIMIT :limit OFFSET :offset
        '''
        command = command % condition
        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_execute_job_log_count(cursor, condition):
        """获取手动执行任务日志数量"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_jobs AS a
        -- 任务ID对应最新的执行ID
        LEFT JOIN (
        SELECT a.job_id, MAX(a.exec_id) AS exec_id
        FROM tb_execute_detail AS a
        GROUP BY job_id
        ) AS b USING(job_id)
        LEFT JOIN tb_execute AS c USING(exec_id)
        LEFT JOIN tb_exec_host AS d USING(server_id)
        %s
        '''
        command = command % condition
        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def get_execute_job_history(cursor, job_id, condition, page, limit):
        """获取任务历史日志列表"""
        command = '''
        SELECT b.exec_id, a.job_name, a.job_index, c.exec_type, c.insert_time, c.update_time,
        c.update_time - c.insert_time AS timedelta, d.server_host, a.server_dir, a.server_script,
        b.`status`
        FROM tb_jobs AS a
        LEFT JOIN tb_execute_detail AS b USING(job_id)
        LEFT JOIN tb_execute AS c USING(exec_id)
        LEFT JOIN tb_exec_host AS d USING(server_id)
        WHERE a.job_id = :job_id %s
        ORDER BY b.exec_id DESC
        LIMIT :limit OFFSET :offset
        '''
        command = command % condition
        result = cursor.query(command, {
            'job_id': job_id,
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_execute_job_history_count(cursor, job_id, condition):
        """获取任务历史日志列表数量"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_jobs AS a
        LEFT JOIN tb_execute_detail AS b USING(job_id)
        LEFT JOIN tb_execute AS c USING(exec_id)
        LEFT JOIN tb_exec_host AS d USING(server_id)
        WHERE a.job_id = :job_id %s
        ORDER BY b.exec_id DESC
        '''
        command = command % condition
        result = cursor.query_one(command, {
            'job_id': job_id
        })
        return result['count'] if result else 0

    @staticmethod
    def get_execute_flow_detail(cursor, exec_id):
        """获取任务流执行详情"""
        command = '''
        SELECT a.id, c.interface_id, job_id, job_name, a.server_host, a.server_dir, a.server_script, a.position,
        a.`status`, a.insert_time, a.update_time, a.update_time - a.insert_time AS timedelta,
        IFNULL((a.insert_time - b.insert_time) / (b.update_time - b.insert_time), 0) AS margin_left,
        IFNULL((a.update_time - a.insert_time) / (b.update_time - b.insert_time), 0) AS width
        FROM tb_execute_detail AS a
        LEFT JOIN tb_execute AS b USING(exec_id)
        LEFT JOIN tb_jobs AS c USING(job_id)
        WHERE exec_id = :exec_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })
        return result if result else []

    @staticmethod
    def get_execute_detail_by_status(cursor, exec_id, status):
        """获取执行详情-by任务状态"""
        command = '''
        SELECT job_id, a.in_degree, a.out_degree, server_host, server_dir,
        server_script, position, a.`level`, a.`status`, params_value, return_code, pid, interface_id
        FROM tb_execute_detail AS a
        INNER JOIN tb_execute AS b USING(exec_id)
        INNER JOIN tb_execute_interface AS c USING(interface_id)
        WHERE a.exec_id = :exec_id AND a.`status` = :status
        '''
        result = cursor.query(command, {
            'exec_id': exec_id,
            'status': status
        })
        return result if result else []

    @staticmethod
    def get_execute_job_log_by_id(cursor, exec_id, job_id):
        """获取任务执行日志"""
        command = '''
        SELECT a.interface_id, job_id, job_name,`level`, message
        FROM tb_schedule_detail_logs AS a
        LEFT JOIN tb_jobs USING(job_id)
        WHERE exec_id = :exec_id AND job_id = :job_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id,
            'job_id': job_id
        })
        return result if result else []

    @staticmethod
    def get_execute_log(cursor, exec_id):
        """获取执行日志"""
        command = '''
        SELECT a.interface_id, job_id, job_name, `level`, message
        FROM tb_schedule_detail_logs AS a
        LEFT JOIN tb_jobs AS b USING(job_id)
        WHERE exec_id = :exec_id
        -- 全局日志只显示5行
        GROUP BY CONCAT(job_id, id %% 5)
        ORDER BY id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })
        return result if result else []

    @staticmethod
    def get_execute_interface_graph(cursor, exec_id):
        """获取执行任务流拓扑结构"""
        command = '''
        SELECT interface_id AS id, interface_name AS name, in_degree, out_degree, `level`, `status`
        FROM tb_execute_interface
        LEFT JOIN tb_interface AS b USING(interface_id)
        WHERE exec_id = :exec_id AND is_tree = 1
            '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })

        return result if result else []

    @staticmethod
    def get_execute_jobs_graph(cursor, exec_id, interface_id):
        """获取执行任务拓扑结构"""
        command = '''
        SELECT job_id AS id, job_name AS name, in_degree, out_degree, `level`, `status`
        FROM tb_execute_detail AS a
        LEFT JOIN tb_jobs AS b USING(job_id)
        WHERE exec_id = :exec_id AND a.interface_id = :interface_id
        '''
        result = cursor.query(command, {
            'exec_id': exec_id,
            'interface_id': interface_id
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
        SET is_push = 1, update_time = :update_time
        WHERE exec_id = :exec_id
        '''
        result = cursor.update(command, {
            'exec_id': exec_id,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def get_exec_dispatch_id(cursor, exec_id):
        """获取执行表中调度id"""
        command = '''
        SELECT exec_type, dispatch_id, interface_id, run_date, is_after, date_format
        FROM tb_execute AS a
        LEFT JOIN tb_dispatch AS b USING(dispatch_id)
        WHERE a.exec_id = :exec_id
        '''
        result = cursor.query_one(command, {
            'exec_id': exec_id
        })
        return result

    @staticmethod
    def add_exec_interface(cursor, data):
        """添加执行任务流依赖表"""
        command = '''
        INSERT INTO tb_execute_interface(exec_id, interface_id, in_degree, out_degree,
        `level`, is_tree, `status`, insert_time, update_time)
        VALUES (:exec_id, :interface_id, :in_degree, :out_degree, :level, :is_tree, :status, :insert_time, :update_time)
        '''
        result = cursor.insert(command, args=data)
        return result

    @staticmethod
    def get_exec_interface_by_exec_id(cursor, exec_id):
        """获取执行任务流依赖表by执行id"""
        command = '''
        SELECT interface_id, in_degree, out_degree, `level`, `status`
        FROM tb_execute_interface
        WHERE exec_id = :exec_id AND is_tree = 1
        '''
        result = cursor.query(command, {
            'exec_id': exec_id
        })
        return result if result else []

    @staticmethod
    def update_exec_interface_status(cursor, exec_id, interface_id, status):
        """修改执行任务流状态"""
        command = '''
        UPDATE tb_execute_interface
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
    def delete_execute(cursor, exec_id):
        """删除执行主表数据"""
        command = '''
        DELETE FROM tb_execute
        WHERE exec_id = :exec_id
        '''
        result = cursor.delete(command, {
            'exec_id': exec_id
        })
        return result

    @staticmethod
    def delete_exec_interface(cursor, exec_id):
        """删除执行任务流表"""
        command = '''
        DELETE FROM tb_execute_interface
        WHERE exec_id = :exec_id
        '''
        result = cursor.delete(command, {
            'exec_id': exec_id
        })
        return result

    @staticmethod
    def delete_exec_detail(cursor, exec_id):
        """删除执行详情表"""
        command = '''
        DELETE FROM tb_execute_detail
        WHERE exec_id = :exec_id
        '''
        result = cursor.delete(command, {
            'exec_id': exec_id
        })
        return result
