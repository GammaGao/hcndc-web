# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class FtpEventModel(object):
    @staticmethod
    def get_ftp_event_list(cursor, condition, page=1, limit=10):
        """获取文件事件列表"""
        command = '''
        SELECT ftp_event_id, event_name, data_path, file_name, start_time, end_time, interval_value, date_time,
        `status`, b.next_run_time, c.ftp_name
        FROM tb_file_event AS a
        LEFT JOIN tb_scheduler AS b ON CONCAT('ftp_event_', a.ftp_event_id) = b.id
        LEFT JOIN tb_ftp_config AS c ON a.ftp_id = c.ftp_id AND c.is_deleted = 0
        %s
        LIMIT :limit OFFSET :offset
        '''
        command = command % condition

        result = cursor.query(command, {
            'limit': limit,
            'offset': (page - 1) * limit
        })
        return result if result else []

    @staticmethod
    def get_ftp_event_list_count(cursor, condition):
        """获取文件事件列表条数"""
        command = '''
        SELECT COUNT(*) AS count
        FROM tb_file_event
        %s
        '''
        command = command % condition
        result = cursor.query_one(command)
        return result['count'] if result else 0

    @staticmethod
    def get_ftp_event_detail(cursor, ftp_event_id):
        """获取文件事件详情"""
        command = '''
        SELECT ftp_event_id, event_name, event_desc, ftp_id, data_path, file_name, start_time, end_time,
        date_time, interval_value, `status`
        FROM tb_file_event
        WHERE ftp_event_id = :ftp_event_id
        '''
        result = cursor.query_one(command, {
            'ftp_event_id': ftp_event_id
        })
        return result if result else {}

    @staticmethod
    def get_ftp_event_interface(cursor, ftp_event_id):
        """获取文件事件中任务流"""
        command = '''
        SELECT b.interface_id
        FROM tb_file_event_interface AS a
        LEFT JOIN tb_interface AS b ON a.interface_id = b.interface_id AND b.is_deleted = 0
        WHERE a.ftp_event_id = :ftp_event_id
        '''
        result = cursor.query(command, {
            'ftp_event_id': ftp_event_id
        })
        return [item['interface_id'] for item in result] if result else []

    @staticmethod
    def update_ftp_event_detail(cursor, ftp_event_id, event_name, event_desc, ftp_id, data_path, file_name,
                                interval_value, start_time, end_time, date_time, new_status, user_id):
        """修改文件事件详情"""
        command = '''
        UPDATE tb_file_event
        SET event_name = :event_name, event_desc = :event_desc, ftp_id = :ftp_id, data_path = :data_path,
        file_name = :file_name, interval_value = :interval_value, start_time = :start_time, end_time = :end_time, 
        date_time = :date_time, `status` = :new_status, updater_id = :user_id, update_time = :update_time
        WHERE ftp_event_id = :ftp_event_id
        '''
        result = cursor.update(command, {
            'ftp_event_id': ftp_event_id,
            'event_name': event_name,
            'event_desc': event_desc,
            'ftp_id': ftp_id,
            'data_path': data_path,
            'file_name': file_name,
            'start_time': start_time,
            'end_time': end_time,
            'date_time': date_time,
            'interval_value': interval_value,
            'new_status': new_status,
            'user_id': user_id,
            'update_time': int(time.time())
        })
        return result

    @staticmethod
    def delete_file_event_interface(cursor, ftp_event_id):
        """删除文件事件任务流"""
        command = '''
        DELETE FROM tb_file_event_interface
        WHERE ftp_event_id = :ftp_event_id
        '''
        result = cursor.delete(command, {
            'ftp_event_id': ftp_event_id
        })
        return result

    @staticmethod
    def add_file_event_interface(cursor, insert_data):
        """新增文件事件任务流"""
        command = '''
        INSERT INTO tb_file_event_interface(ftp_event_id, interface_id)
        VALUES(:ftp_event_id, :interface_id)
        '''
        result = cursor.insert(command, insert_data)
        return result

    @staticmethod
    def add_ftp_event_detail(cursor, event_name, event_desc, ftp_id, data_path, file_name,
                             interval_value, start_time, end_time, date_time, user_id):
        """新增文件事件"""
        command = '''
        INSERT INTO tb_file_event(event_name, event_desc, ftp_id, data_path, file_name, interval_value, start_time,
        end_time, date_time, creator_id, updater_id, insert_time, update_time, `status`)
        VALUES(:event_name, :event_desc, :ftp_id, :data_path, :file_name, :interval_value, :start_time, :end_time,
        :date_time, :user_id, :user_id, :data_time, :data_time, 1)
        '''
        result = cursor.insert(command, {
            'event_name': event_name,
            'event_desc': event_desc,
            'ftp_id': ftp_id,
            'data_path': data_path,
            'file_name': file_name,
            'interval_value': interval_value,
            'start_time': start_time,
            'end_time': end_time,
            'date_time': date_time,
            'user_id': user_id,
            'data_time': int(time.time())
        })
        return result
