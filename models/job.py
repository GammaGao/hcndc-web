# !/usr/bin/env python
# -*- coding: utf-8 -*-


class JobModel(object):
    @staticmethod
    def get_job_list(cursor, condition, page=1, limit=10):
        """获取任务列表"""
        command = '''
        SELECT job_id, interface_id, job_name, job_desc, server_id,
        server_dir, server_script, is_deleted
        FROM tb_jobs
        %s
        ORDER BY job_id
        LIMIT :limit OFFSET :offset
        
        '''

        command = command % condition

        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_job_count(cursor, condition):
        """获取任务条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_jobs
        %s
        '''

        command = command % condition

        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def is_alive_job(cursor, job_id):
        """是否在任务以来表中"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_job_prep
        WHERE is_deleted = 0 AND (job_id = :job_id OR prep_id = :job_id)
        '''

        result = cursor.query_one(command, {
            'job_id': job_id
        })
        return result['count'] if result else 0

    @staticmethod
    def delete_job(cursor, job_id, user_id):
        """删除项目"""
        command = '''
        UPDATE tb_jobs
        SET is_deleted = 1, updater_id = :user_id, update_time = UNIX_TIMESTAMP()
        WHERE job_id = :job_id
        '''

        result = cursor.update(command, {
            'job_id': job_id,
            'user_id': user_id
        })
        return result

    @staticmethod
    def get_job_detail(cursor, job_id):
        """获取任务详情"""
        command = '''
        SELECT a.job_id, interface_id, job_name, job_desc, server_name,
        b.server_id, server_host, server_dir, server_script, a.is_deleted,
        GROUP_CONCAT(DISTINCT c.prep_id) AS prep_id, GROUP_CONCAT(DISTINCT d.param_id) AS param_id
        FROM tb_jobs AS a
        LEFT JOIN tb_exec_host AS b ON a.server_id = b.server_id AND b.is_deleted = 0
        LEFT JOIN tb_job_prep AS c ON a.job_id = c.job_id AND c.is_deleted = 0
        LEFT JOIN tb_job_param AS d ON a.job_id = d.job_id AND d.is_deleted = 0
        WHERE a.job_id = :job_id
        '''

        result = cursor.query_one(command, {
            'job_id': job_id
        })
        return result if result else {}

    @staticmethod
    def update_job_detail(cursor, job_id, interface_id, job_name, job_desc, server_id, server_dir, server_script,
                          user_id, is_deleted):
        """修改任务详情"""
        command = '''
        UPDATE tb_jobs
        SET job_name = :job_name, interface_id = :interface_id, job_desc = :job_desc, server_id = :server_id,
        server_dir = :server_dir, server_script = :server_script, update_time = UNIX_TIMESTAMP(),
        updater_id = :user_id, is_deleted = :is_deleted
        WHERE job_id = :job_id
        '''

        result = cursor.update(command, {
            'job_id': job_id,
            'interface_id': interface_id,
            'job_name': job_name,
            'job_desc': job_desc,
            'server_id': server_id,
            'server_dir': server_dir,
            'server_script': server_script,
            'user_id': user_id,
            'is_deleted': is_deleted
        })
        return result

    @staticmethod
    def add_job_detail(cursor, job_name, interface_id, job_desc, server_id, server_dir, server_script, user_id):
        """新增任务详情"""
        command = '''
        INSERT INTO tb_jobs(interface_id, job_name, job_desc, server_id, server_dir, server_script,
        insert_time, update_time, creator_id, updater_id)
        VALUES (:interface_id, :job_name, :job_desc, :server_id, :server_dir, :server_script,
        UNIX_TIMESTAMP(), UNIX_TIMESTAMP(),
        :user_id, :user_id
        )
        '''

        result = cursor.insert(command, {
            'job_name': job_name,
            'interface_id': interface_id,
            'job_desc': job_desc,
            'server_id': server_id,
            'server_dir': server_dir,
            'server_script': server_script,
            'user_id': user_id
        })
        return result

    @staticmethod
    def get_job_list_all(cursor):
        """获取所有任务列表"""
        command = '''
        SELECT job_id, job_name
        FROM tb_jobs
        WHERE is_deleted = 0
        '''

        result = cursor.query(command)
        return result if result else []

    @staticmethod
    def get_job_list_all_by_interface(cursor, interface_id):
        """获取接口下所有任务列表"""
        command = '''
        SELECT job_id, job_name
        FROM tb_jobs
        WHERE is_deleted = 0 AND interface_id = :interface_id
        '''
        result = cursor.query(command, {
            'interface_id': interface_id
        })
        return result if result else []

    @staticmethod
    def add_job_prep(cursor, data):
        """新增任务依赖-批量"""
        command = '''
        INSERT INTO tb_job_prep(job_id, prep_id, insert_time, update_time, creator_id, updater_id)
        VALUES (:job_id, :prep_id, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), :user_id, :user_id)
        '''

        result = cursor.insert(command, args=data)
        return result

    @staticmethod
    def delete_job_prep(cursor, data):
        """删除任务依赖-批量"""
        command = '''
        UPDATE tb_job_prep
        SET is_deleted = 1, updater_id = :user_id, update_time = UNIX_TIMESTAMP()
        WHERE job_id = :job_id AND prep_id = :prep_id
        '''
        result = cursor.update(command, args=data)
        return result

    @staticmethod
    def add_job_param(cursor, data):
        """新增任务参数-批量"""
        command = '''
        INSERT INTO tb_job_param(job_id, param_id, insert_time, update_time, creator_id, updater_id)
        VALUES (:job_id, :param_id, :insert_time, :update_time, :user_id, :user_id)
        '''

        result = cursor.insert(command, args=data)
        return result

    @staticmethod
    def delete_job_param(cursor, data):
        """删除任务参数-批量"""
        command = '''
        UPDATE tb_job_param
        SET is_deleted = 1, updater_id = :user_id, update_time = :update_time
        WHERE job_id = :job_id AND param_id = :param_id
        '''
        result = cursor.update(command, args=data)
        return result

    @staticmethod
    def get_job_params_by_job_id(cursor, job_id):
        """获取任务参数"""
        command = '''
        SELECT param_type, param_value, source_type, auth_type, source_host,
        source_port, source_database, source_user, source_password
        FROM tb_job_param AS a
        LEFT JOIN tb_param_config AS b ON a.param_id = b.param_id AND b.is_deleted = 0
        LEFT JOIN tb_datasource AS c ON b.source_id = c.source_id AND c.is_deleted = 0
        WHERE job_id = :job_id AND a.is_deleted = 0
        '''
        result = cursor.query(command, {
            'job_id': job_id
        })
        return result if result else []
