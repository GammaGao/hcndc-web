# !/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import csv
import time
import xlrd
from flask import render_template, session, redirect, request, jsonify, send_file

from configs import app, db
from models.base import ExecHostModel
from models.interface import InterfaceModel
from models.job import JobModel
from models.params import ParamsModel
from util import session as curr_session


@app.route('/job/')
def Job():
    """任务列表"""
    if session.get('login'):
        return render_template('job/job_list.html')
    return redirect('/login/')


@app.route('/job/detail/<int:id>/')
def JobDetail(id):
    """任务详情"""
    if session.get('login'):
        return render_template('job/job_detail.html', job_id=id)
    return redirect('/login/')


@app.route('/job/update/<int:id>/')
def JobUpdate(id):
    """任务修改"""
    if session.get('login'):
        return render_template('job/job_update.html', job_id=id)
    return redirect('/login/')


@app.route('/job/add/')
def JobAdd():
    """新增任务"""
    if session.get('login'):
        return render_template('job/job_add.html')
    return redirect('/login/')


@app.route('/job/download/', methods=['GET', 'POST'])
def JobDownload():
    """下载任务模板文件"""
    file_path = './download/新增任务模板.xlsx'
    response = send_file(file_path, as_attachment=True, attachment_filename='新增任务模板.xlsx')
    return response


@app.route('/job/upload/', methods=['POST'])
def JobUpload():
    """上传任务配置文件"""
    # 文件路径
    file_dir = './uploads'
    # 文件类型
    file_type = {'xlsx', 'xls', 'csv'}
    # 异常类型
    err_type = {
        0: '第%s行[序号]参数不为整型',
        1: '第%s行[所属任务流id]参数不为整型',
        2: '第%s行[任务名称]参数不为字符串类型',
        3: '第%s行[任务描述]参数不为字符串类型',
        4: '第%s行[服务器id]参数不为整型',
        5: '第%s行[任务目录]参数不为字符串类型',
        6: '第%s行[脚本目录]参数不为字符串类型',
        7: '第%s行[脚本命令]参数不为字符串类型',
        8: '第%s行[依赖任务序号(本次新建任务)]参数不为整型或没按逗号分隔',
        9: '第%s行[依赖任务id(已有任务)]参数不为空或整型或没按逗号分隔',
        10: '第%s行[任务参数]不为空或整型或没按逗号分隔',
        11: '第%s行[返回值]参数不为整型'
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
                # 取前12列
                data.append(sheet.row_values(i)[:12])
        # csv文件
        else:
            data = []
            with open(file_path, "r") as csv_file:
                reader = csv.reader(csv_file)
                for index, line in enumerate(reader):
                    if index > 0:
                        # 取前12列
                        data.append(line[:12])
        # 异常原因
        err_msg = []
        # 任务流id列表
        interface_result = InterfaceModel.get_interface_id_list(db.etl_db)
        interface_ids = [i['interface_id'] for i in interface_result]
        # 服务器id列表
        exec_host_result = ExecHostModel.get_exec_host_all(db.etl_db)
        exec_host_ids = [i['server_id'] for i in exec_host_result]
        # 依赖任务序号(本次新建任务)列表
        curr_job_num = []
        # 依赖任务id(已有任务)列表
        job_result = JobModel.get_job_list_all(db.etl_db)
        job_ids = [i['job_id'] for i in job_result]
        # 任务参数列表
        job_params = ParamsModel.get_params_all(db.etl_db)
        job_params_ids = [i['param_id'] for i in job_params]
        # 文件为空
        if not data:
            err_msg.append('文件为空')
        for index, row in enumerate(data):
            # Excel行号
            row_num = index + 2
            # 校验列数
            if len(row) < 10:
                err_msg.append('第%s行参数个数小于10个' % row_num)
            else:
                # 校验并处理每列参数
                for i, param in enumerate(row):
                    try:
                        # int类型参数
                        if i in [0, 1, 4, 11]:
                            row[i] = int(param)
                        # 字符串类型参数
                        elif i in [2, 3, 5, 6, 7]:
                            row[i] = str(param)
                        # 依赖任务
                        else:
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
                    # 添加任务[序号]
                    if i == 0 and isinstance(param, int):
                        curr_job_num.append(param)
                    # [所属任务流id]判空
                    if i == 1 and isinstance(param, int):
                        if param not in interface_ids:
                            err_msg.append('第%s行[所属任务流id]不存在' % row_num)
                    # [任务名称]判空
                    if i == 2 and param == '':
                        err_msg.append('第%s行[任务名称]参数不得为空' % row_num)
                    # [任务名称]数据库查重
                    if i == 2 and param != '':
                        if JobModel.get_job_detail_by_name(db.etl_db, param):
                            err_msg.append('第%s行[任务名称]参数已存在数据库中' % row_num)
                    # [服务器id]判空
                    if i == 4 and isinstance(param, int):
                        if param not in exec_host_ids:
                            err_msg.append('第%s行[服务器id]不存在' % row_num)
                    # [任务目录]判空和","字符串
                    if i == 5:
                        if param == '':
                            err_msg.append('第%s行[任务目录]参数不得为空' % row_num)
                        elif re.findall(',', param):
                            err_msg.append('第%s行[任务目录]参数不得出现逗号字符","' % row_num)
                    # [脚本目录]判空
                    if i == 6 and param == '':
                        err_msg.append('第%s行[脚本目录]参数不得为空' % row_num)
                    # [脚本命令]判空
                    if i == 7 and param == '':
                        err_msg.append('第%s行[脚本命令]参数不得为空' % row_num)
                    # [依赖任务序号(本次新建任务)]数据库判空
                    if i == 8 and isinstance(param, list):
                        for job_num in param:
                            if job_num not in curr_job_num:
                                err_msg.append('第%s行[依赖任务序号(本次新建任务)][%s]不存在' % (row_num, job_num))
                    # [依赖任务id(已有任务)]数据库判空
                    if i == 9 and isinstance(param, list):
                        for job_id in param:
                            if job_id not in job_ids:
                                err_msg.append('第%s行[依赖任务id(已有任务)][%s]不存在' % (row_num, job_id))
                    # [任务参数]数据库判空
                    if i == 10 and isinstance(param, list):
                        for job_param in param:
                            if job_param not in job_params_ids:
                                err_msg.append('第%s行[任务参数][%s]不存在' % (row_num, job_param))

        # [序号]是否重复
        serial_num = [row[0] for row in data]
        if len(serial_num) != len(set(serial_num)):
            err_msg.append('该文件中[序号]存在重复')

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
            # 依赖任务序号 -> 任务id映射
            job_map = {}
            # 新增任务详情
            for line in data:
                job_id = JobModel.add_job_detail(db.etl_db, line[2], line[1], line[3], line[5], line[4], line[6],
                                                 line[7], line[11], user_id)
                job_map[line[0]] = job_id
                # 表格数据中新增任务id字段
                line.append(job_id)
            # 新增任务依赖
            prep_data = []
            for line in data:
                prep_job = []
                # 本次新增任务序号与任务id映射
                if line[8]:
                    prep_job = [job_map[i] for i in line[8]]
                if line[9]:
                    # 合并数组
                    prep_job += line[9]
                for prep_id in prep_job:
                    prep_data.append({
                        # 最后一位为新增的任务id字段
                        'job_id': line[len(line) - 1],
                        'prep_id': prep_id,
                        'user_id': user_id,
                        'insert_time': int(time.time()),
                        'update_time': int(time.time())
                    })
            if prep_data:
                JobModel.add_job_prep(db.etl_db, prep_data)
            # 新增任务参数
            job_params = []
            for line in data:
                for param_id in line[10]:
                    job_params.append({
                        # 最后一位为新增的任务id字段
                        'job_id': line[len(line) - 1],
                        'param_id': param_id,
                        'insert_time': int(time.time()),
                        'update_time': int(time.time()),
                        'user_id': user_id
                    })
            if job_params:
                JobModel.add_job_param(db.etl_db, job_params)
            # 删除文件
            os.remove(file_path)
            return jsonify({'status': 200, 'msg': '成功', 'data': {}})
    else:
        return jsonify({'status': 400, 'msg': '文件类型错误', 'data': {}})
