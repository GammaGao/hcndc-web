# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import csv
import xlrd
import time
import datetime
from datetime import date, timedelta

from configs import app, db
from models.interface import InterfaceModel
from flask import render_template, session, redirect, request, jsonify, send_file
from util import session as curr_session


@app.route('/interface/')
def Interface():
    """任务流列表"""
    if session.get('login'):
        return render_template('interface/interface_list.html')
    return redirect('/login/')


@app.route('/interface/detail/<int:interface_id>/')
def InterfaceDetail(interface_id):
    """任务流详情"""
    if session.get('login'):
        return render_template('interface/interface_detail.html', interface_id=interface_id)
    return redirect('/login/')


@app.route('/interface/update/<int:interface_id>/')
def InterfaceUpdate(interface_id):
    """任务流修改"""
    if session.get('login'):
        return render_template('interface/interface_update.html', interface_id=interface_id)
    return redirect('/login/')


@app.route('/interface/add/')
def InterfaceAdd():
    """新增任务流"""
    if session.get('login'):
        return render_template('interface/interface_add.html')
    return redirect('/login/')


@app.route('/test/')
def AllJobShow():
    """所有任务展示"""
    return render_template('test.html')


@app.route('/interface/download/', methods=['GET', 'POST'])
def InterfaceDownload():
    """下载任务流模板文件"""
    file_path = './download/新增任务流模板.xlsx'
    response = send_file(file_path, as_attachment=True, attachment_filename='新增任务流模板.xlsx')
    return response


@app.route('/interface/upload/', methods=['POST'])
def InterfaceUpload():
    """上传任务流配置文件"""
    # 文件路径
    file_dir = './uploads'
    # 文件类型
    file_type = {'xlsx', 'xls', 'csv'}
    # 异常类型
    err_type = {
        0: '第%s行[序号]参数不为整型',
        1: '第%s行[任务流名称]参数不为字符串类型',
        2: '第%s行[任务流描述]参数不为字符串类型',
        3: '第%s行[任务流目录]参数不为字符串类型',
        5: '第%s行[重试次数]参数不为整型',
        6: '第%s行[依赖任务流序号(本次新建任务流)]参数不为整型或没按逗号分隔',
        7: '第%s行[依赖任务流id(已有任务流)]参数不为空或整型或没按逗号分隔'
    }
    file = request.files['file']
    # 获取文件名
    file_name = file.filename
    # 获取文件后缀
    file_suffix = '.' in file_name and file_name.rsplit('.', 1)[1]
    if file and file_suffix in file_type:
        # 保存文件到upload目录
        file_path = os.path.join(file_dir, file_name)
        file.save(file_path)
        # 异常原因
        err_msg = []
        # excel文件
        if file_suffix in {'xlsx', 'xls'}:
            data = xlrd.open_workbook(file_path)
            # 只取第一个sheet
            sheet = data.sheet_by_name(data.sheet_names()[0])
            # 从第2行开始读取
            data = []
            for i in range(1, sheet.nrows):
                # 取前8列
                item = sheet.row_values(i)[:8]
                try:
                    # 日期格式转换
                    if item[4]:
                        item[4] = xlrd.xldate_as_tuple(item[4], 0)
                        item[4] = datetime.date(*item[4][:3]).strftime('%Y-%m-%d')
                    else:
                        item[4] = None
                except:
                    item[4] = None
                    err_msg.append('第%s行[数据日期]参数格式错误' % (i + 1))
                data.append(item)
        # csv文件
        else:
            data = []
            with open(file_path, "r") as csv_file:
                reader = csv.reader(csv_file)
                for index, line in enumerate(reader):
                    if index > 0:
                        # 取前8列
                        item = line[:8]
                        try:
                            # 日期格式转换
                            date_value = re.findall(r'(\d{4}).(\d{1,2}).(\d{1,2})', item[4])
                            if date_value:
                                item[4] = '%04d-%02d-%02d' % tuple(int(item) for item in date_value[0])
                            else:
                                item[4] = (date.today() + timedelta(days=-1)).strftime('%Y-%m-%d')
                        except:
                            item[4] = None
                            err_msg.append('第%s行[数据日期]参数格式错误' % (index + 1))
                        data.append(item)
        # 任务流id列表
        interface_result = InterfaceModel.get_interface_id_list(db.etl_db)
        interface_ids = [i['interface_id'] for i in interface_result]
        # 文件为空
        if not data:
            err_msg.append('文件为空')
        # [依赖任务流序号(本次新建任务流)]列表
        curr_interface_num = []
        for index, row in enumerate(data):
            # Excel行号
            row_num = index + 2
            # 校验列数
            if len(row) < 8:
                err_msg.append('第%s行参数个数小于8个' % row_num)
            else:
                # 校验并处理每列参数
                for i, param in enumerate(row):
                    try:
                        # int类型参数
                        if i in [0, 5]:
                            row[i] = int(param)
                            # 添加[依赖任务流序号(本次新建任务流)]
                            if i == 0:
                                curr_interface_num.append(row[i])
                        # 字符串类型参数
                        elif i in [1, 2, 3]:
                            row[i] = str(param)
                        # 依赖任务流
                        elif i in [6, 7]:
                            if isinstance(param, str):
                                if param != '':
                                    row[i] = [int(i) for i in str(param).split(',')]
                                else:
                                    row[i] = []
                            else:
                                row[i] = [int(param)]
                    except:
                        err_msg.append(err_type[i] % row_num)
                for i, param in enumerate(row):
                    # [任务流名称]判空
                    if i == 1 and param == '':
                        err_msg.append('第%s行[任务流名称]参数不得为空' % row_num)
                    # [任务流名称]数据库查重
                    if i == 1 and param != '':
                        if InterfaceModel.get_interface_detail_by_name(db.etl_db, param):
                            err_msg.append('第%s行[任务流名称]参数已存在数据库中' % row_num)
                    # [任务流目录]判空
                    if i == 3 and param == '':
                        err_msg.append('第%s行[任务流目录]参数不得为空' % row_num)
                    # [重试次数]次数限制
                    if i == 5 and isinstance(param, int) and (param < 0 or param > 10):
                        err_msg.append('第%s行[重试次数]参数请限制在0-10之内' % row_num)
                    # [依赖任务流序号(本次新建任务流)]判空
                    if i == 6 and isinstance(param, list):
                        for item in param:
                            if item not in curr_interface_num:
                                err_msg.append('第%s行[依赖任务流序号(本次新建任务流)][%s]不存在' % (row_num, item))
                    # [依赖任务流id(已有任务流)]数据库判空
                    if i == 7 and isinstance(param, list):
                        for item in param:
                            if item not in interface_ids:
                                err_msg.append('第%s行[依赖任务流id(已有任务流)][%s]不存在' % (row_num, item))

        # [序号]是否重复
        serial_num = [row[0] for row in data]
        if len(serial_num) != len(set(serial_num)):
            err_msg.append('该文件中[序号]存在重复')

        # [任务流名称]文件内查重
        serial_name = [row[1] for row in data]
        if len(serial_name) != len(set(serial_name)):
            err_msg.append('该文件中[任务流名称]存在重复')
        # 返回异常信息
        if err_msg:
            # 删除文件
            os.remove(file_path)
            return jsonify({'status': 401, 'msg': '文件参数错误', 'data': {'err_msg': err_msg}})
        # 写入数据库
        else:
            # 用户id
            user_info = curr_session.get_info()
            user_id = user_info['id']
            # 依赖任务流序号 -> 任务流id映射
            interface_map = {}
            for item in data:
                # 新增任务流
                interface_id = InterfaceModel.add_interface(db.etl_db, item[1], item[2], item[3], item[4], item[5],
                                                            user_id)
                # 添加映射
                interface_map[item[0]] = interface_id
                # 表格数据中新增任务流id字段
                item.append(interface_id)
            # 新增任务流依赖
            parent_arr = []
            for line in data:
                parent_interface = []
                # [依赖任务流序号(本次新建任务流)]映射
                if line[6]:
                    parent_interface = [interface_map[i] for i in line[6]]
                # [依赖任务流id(已有任务流)]
                if line[7]:
                    # 合并数组
                    parent_interface += line[7]
                for parent_id in parent_interface:
                    parent_arr.append({
                        # 最后一位为新增的任务id字段
                        'interface_id': line[len(line) - 1],
                        'parent_id': parent_id,
                        'insert_time': int(time.time()),
                        'update_time': int(time.time()),
                        'creator_id': user_id,
                        'updater_id': user_id
                    })
            InterfaceModel.add_interface_parent(db.etl_db, parent_arr) if parent_arr else None
            # 删除文件
            os.remove(file_path)
            return jsonify({'status': 200, 'msg': '成功', 'data': {}})
    else:
        return jsonify({'status': 400, 'msg': '文件类型错误', 'data': {}})
