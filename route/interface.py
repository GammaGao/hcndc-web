# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import csv
import xlrd
import time
import datetime

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


@app.route('/interface/detail/<int:id>/')
def InterfaceDetail(id):
    """任务流详情"""
    if session.get('login'):
        return render_template('interface/interface_detail.html', interface_id=id)
    return redirect('/login/')


@app.route('/interface/update/<int:id>/')
def InterfaceUpdate(id):
    """任务流修改"""
    if session.get('login'):
        return render_template('interface/interface_update.html', interface_id=id)
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
        0: '第%s行[任务流名称]参数不为字符串类型',
        1: '第%s行[任务流描述]参数不为字符串类型',
        2: '第%s行[任务流目录]参数不为字符串类型',
        4: '第%s行[重试次数]参数不为整型'
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
        # excel文件
        if file_suffix in {'xlsx', 'xls'}:
            data = xlrd.open_workbook(file_path)
            # 只取第一个sheet
            sheet = data.sheet_by_name(data.sheet_names()[0])
            # 从第2行开始读取
            data = []
            for i in range(1, sheet.nrows):
                # 取前5列
                item = sheet.row_values(i)[:5]
                # 日期格式转换
                item[3] = xlrd.xldate_as_tuple(item[3], 0)
                item[3] = datetime.date(*item[3][:3]).strftime('%Y-%m-%d')
                data.append(item)
        # csv文件
        else:
            data = []
            with open(file_path, "r") as csv_file:
                reader = csv.reader(csv_file)
                for index, line in enumerate(reader):
                    if index > 0:
                        # 取前5列
                        item = line[:5]
                        # 日期格式转换
                        date_value = re.findall(r'(\d{4}).(\d{1,2}).(\d{1,2})', item[3])
                        if date_value:
                            item[3] = '%04d-%02d-%02d' % tuple(int(item) for item in date_value[0])
                        else:
                            item[3] = ''
                        data.append(line[:5])

        # 异常原因
        err_msg = []
        # 文件为空
        if not data:
            err_msg.append('文件为空')
        for index, row in enumerate(data):
            # Excel行号
            row_num = index + 2
            # 校验列数
            if len(row) < 5:
                err_msg.append('第%s行参数个数小于5个' % row_num)
            else:
                # 校验并处理每列参数
                for i, param in enumerate(row):
                    try:
                        # int类型参数
                        if i in [4]:
                            row[i] = int(param)
                        # 字符串类型参数
                        elif i in [0, 1, 2]:
                            row[i] = str(param)
                    except:
                        err_msg.append(err_type[i] % row_num)

                for i, param in enumerate(row):
                    # [任务流名称]判空
                    if i == 0 and param == '':
                        err_msg.append('第%s行[任务流名称]参数不得为空' % row_num)
                    # [任务流名称]数据库查重
                    if i == 0 and param != '':
                        if InterfaceModel.get_interface_detail_by_name(db.etl_db, param):
                            err_msg.append('第%s行[任务流名称]参数已存在' % row_num)
                    # [任务流目录]判空
                    if i == 2 and param == '':
                        err_msg.append('第%s行[任务流目录]参数不得为空' % row_num)
                    # [重试次数]次数限制
                    if i == 3 and isinstance(param, int) and (param < 0 or param > 10):
                        err_msg.append('第%s行[重试次数]参数请限制在0-10之内' % row_num)

        # [任务流名称]文件内查重
        serial_name = [row[0] for row in data]
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
            flow_data = []
            for item in data:
                flow_data.append({
                    'interface_name': item[0],
                    'interface_desc': item[1],
                    'interface_index': item[2],
                    'run_time': item[3],
                    'retry': item[4],
                    'user_id': user_id,
                    'insert_time': int(time.time()),
                    'update_time': int(time.time())
                })
            # 新增任务流
            InterfaceModel.add_interface_many(db.etl_db, flow_data)
            # 删除文件
            os.remove(file_path)
            return jsonify({'status': 200, 'msg': '成功', 'data': {}})
    else:
        return jsonify({'status': 400, 'msg': '文件类型错误', 'data': {}})
