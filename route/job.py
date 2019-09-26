# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app

from flask import render_template, session, redirect, request, jsonify
import os
import xlrd


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


@app.route('/job/upload/', methods=['POST'])
def JobUpload():
    """上传配置文件"""
    file_dir = './uploads'
    file = request.files['file']  # 从表单的file字段获取文件，file为该表单的name值
    # 判断是否是允许上传的文件类型
    file_name = file.filename
    file_suffix = '.' in file_name and file_name.rsplit('.', 1)[1]
    if file and file_suffix in {'xlsx', 'xls', 'csv'}:
        # 校验文件名安全, 但不识别中文, 需要修改源码, 增加部署细节, 放弃
        # fname = secure_filename(f.filename)
        # 保存文件到upload目录
        file_path = os.path.join(file_dir, file_name)
        file.save(file_path)
        # excel文件
        if file_suffix in {'xlsx', 'xls'}:
            data = xlrd.open_workbook(file_path)
            sheet1 = data.sheet_by_name(data.sheet_names()[0])
            for i in range(1, sheet1.nrows):
                print(sheet1.row_values(i))
        else:
            pass
        return jsonify({'status': 200, 'msg': '成功', 'data': {}}), 200
    else:
        return jsonify({'status': 400, 'msg': '文件类型错误', 'data': {}}), 400
