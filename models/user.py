# !/usr/bin/env python
# -*- coding: utf-8 -*-


class UserModel(object):
    @staticmethod
    def get_user_menu(cursor, user_id):
        """获取用户菜单"""
        command = '''
        SELECT tb_user_menu.id, tb_user_menu.menu_name, tb_user_menu.parent_id, tb_user_menu.order_num,
        tb_user_menu.url, tb_user_menu.menu_type, tb_user_menu.icon
        FROM tb_user
        LEFT JOIN tb_user_roles_link ON tb_user.id = tb_user_roles_link.user_id
        LEFT JOIN tb_user_roles ON tb_user_roles_link.role_id = tb_user_roles.id
        LEFT JOIN tb_user_menu_link ON tb_user_roles.id = tb_user_menu_link.role_id
        LEFT JOIN tb_user_menu ON tb_user_menu.id = tb_user_menu_link.menu_id
        WHERE tb_user.id = :user_id AND tb_user_menu.is_deleted = 0
        ORDER BY tb_user_menu.parent_id, tb_user_menu.order_num
        '''

        result = cursor.query(command, {
            'user_id': user_id
        })
        return result if result else []
