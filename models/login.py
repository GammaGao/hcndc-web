# !/usr/bin/env python
# -*- coding: utf-8 -*-

class LoginModel(object):
    @staticmethod
    def get_user(cursor, username, password):
        """用户登录"""
        command = '''
        SELECT tb_user.id, tb_user.user_name, tb_user_roles.`name` as role, GROUP_CONCAT(tb_user_privilege.permission) as permission
        FROM tb_user
        LEFT JOIN tb_user_roles_link ON tb_user.id = tb_user_roles_link.user_id
        LEFT JOIN tb_user_roles ON tb_user_roles_link.role_id = tb_user_roles.id
        LEFT JOIN tb_user_privilege_link ON tb_user_roles.id = tb_user_privilege_link.role_id
        LEFT JOIN tb_user_privilege ON tb_user_privilege_link.privilege_id = tb_user_privilege.id
        WHERE tb_user.user_name = :username AND tb_user.`password` = md5(:password)
        GROUP BY tb_user.id, tb_user.user_name, tb_user_roles.`name`
        '''

        result = cursor.query_one(command, {
            'username': username,
            'password': password
        })
        return result if result else {}
