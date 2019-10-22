# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app, db
from models.datasource import DataSourceModel
from models.params import ParamsModel
from util import session as curr_session

from flask import render_template, session, redirect, request, jsonify
import os
import csv
import time
import xlrd


@app.route('/params/')
def Params():
    """参数列表"""
    if session.get('login'):
        return render_template('params/params_list.html')
    return redirect('/login/')


@app.route('/params/update/<int:id>/')
def ParamsUpdate(id):
    """参数修改"""
    if session.get('login'):
        return render_template('params/params_update.html', param_id=id)
    return redirect('/login/')


@app.route('/params/add/')
def ParamsAdd():
    """新增参数"""
    if session.get('login'):
        return render_template('params/params_add.html')
    return redirect('/login/')


@app.route('/params/upload/', methods=['POST'])
def ParamsUpload():
    """上传任务参数文件"""
    # 文件路径
    file_dir = './uploads'
    # 文件类型
    file_type = {'xlsx', 'xls', 'csv'}
    # 异常类型
    err_type = {
        0: '第%s行[参数类型]不为整型',
        1: '第%s行[参数名称]不为字符串类型',
        2: '第%s行[数据源id]不为整型',
        3: '第%s行[参数值]不为字符串类型',
        4: '第%s行[描述]不为字符串类型'
    }
    file = request.files['file']
    # 获取文件名
    file_name = file.filename
    # 获取文件后缀
    file_suffix = '.' in file_name and file_name.rsplit('.', 1)[1]
    if file and file_suffix in file_type:
        # 校验文件名安全, 但不识别中文, 需要修改源码, 增加部署细节, 放弃
        # fname = secure_filename(f.filename)
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
                data.append(sheet.row_values(i)[:5])
        # csv文件
        else:
            data = []
            with open(file_path, "r") as csv_file:
                reader = csv.reader(csv_file)
                for index, line in enumerate(reader):
                    if index > 0:
                        # 取前5列
                        data.append(line[:5])
        # 异常原因
        err_msg = []
        # 数据源id列表
        source_result = DataSourceModel.get_datasource_list_all(db.etl_db)
        source_ids = [i['source_id'] for i in source_result]
        # 文件为空
        if not data:
            err_msg.append('文件为空')
        for index, row in enumerate(data):
            # Excel行号
            row_num = index + 2
            # 校验列数
            if len(row) < 5:
                err_msg.append('第%s行参数个数小于5个')
            else:
                # 校验并处理每列参数
                for i, param in enumerate(row):
                    try:
                        # int类型参数
                        if i == 0:
                            row[i] = int(param)
                        # 数据源id
                        elif i == 2:
                            row[i] = int(row[i]) if int(row[0]) == 1 else 0
                        # 字符串类型参数
                        elif i in [1, 3, 4]:
                            row[i] = str(param)
                    except:
                        err_msg.append(err_type[i] % row_num)
                for i, param in enumerate(row):
                    # 检验参数类型是否存在
                    if i == 0 and param not in [0, 1]:
                        err_msg.append('第%s行[参数类型]不为0或1' % row_num)
                    # 检验参数名称是否存在
                    if i == 1 and param == '':
                        err_msg.append('第%s行[参数名称]不得为空' % row_num)
                    # 检验参数值是否存在
                    if i == 3 and param == '':
                        err_msg.append('第%s行[参数值]不得为空' % row_num)
                    # 校验数据源id是否存在
                    if i == 2 and int(row[0]) == 1 and isinstance(param, int):
                        if param not in source_ids:
                            err_msg.append('第%s行[数据源id]不存在' % row_num)
        # 返回异常信息
        if err_msg:
            # 删除文件
            os.remove(file_path)
            return jsonify({'status': 401, 'msg': '文件类型错误', 'data': {'err_msg': err_msg}})
        # 写入数据库
        else:
            # 用户id
            user_info = curr_session.get_info()
            user_id = user_info['id']
            params_data = []
            for line in data:
                params_data.append({
                    'param_type': line[0],
                    'param_name': line[1],
                    'source_id': line[2],
                    'param_value': line[3],
                    'param_desc': line[4],
                    'insert_time': int(time.time()),
                    'update_time': int(time.time()),
                    'creator_id': user_id,
                    'updater_id': user_id
                })
            if params_data:
                ParamsModel.add_param_many(db.etl_db, params_data)
            return jsonify({'status': 200, 'msg': '成功', 'data': {}})

    else:
        return jsonify({'status': 400, 'msg': '文件类型错误', 'data': {}})
