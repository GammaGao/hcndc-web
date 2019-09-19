# !/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

from server.decorators import make_decorator


class UserFilter(object):
    @staticmethod
    @make_decorator
    def filter_menu_data(menu_list):
        """菜单数据结构"""
        # 构造字典结构
        menu_dict = {}
        for menu in menu_list:
            menu_dict[menu['id']] = menu

        def get_children_recursion(item):
            """获取子节点"""
            item_children = item.setdefault('children', [])
            # 该节点的所有子节点
            children = [i for i in menu_list if item['id'] == i['parent_id']]
            for child in children:
                # 添加子节点
                item_children.append(child)
                # 递归子节点
                get_children_recursion(child)

        def clear_field(item):
            """清理多余字段"""
            item.pop('id')
            item.pop('parent_id')
            item.pop('order_num')
            # 菜单类型暂时为三级目录
            # item.pop('menu_type')
            for child in item.get('children', []):
                clear_field(child)
            if not item.get('children', []):
                item.pop('children')
            return item

        # 最终结果值
        result = []
        for menu in menu_list:
            # 从导航栏开始递归
            if menu['menu_type'] == 1:
                # 浅拷贝
                get_children_recursion(menu)
                # 深拷贝
                items = clear_field(copy.deepcopy(menu))
                result.append(items)

        return {'status': 200, 'msg': '成功', 'data': {'menu': result}}, 200
