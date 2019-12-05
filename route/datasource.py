# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app

from flask import render_template, session, redirect


@app.route('/datasource/')
def DataSource():
    """数据源列表"""
    if session.get('login'):
        return render_template('datasource/datasource_list.html')
    return redirect('/login/')


@app.route('/datasource/update/<int:source_id>/')
def DataSourceUpdate(source_id):
    """数据源修改"""
    if session.get('login'):
        return render_template('datasource/datasource_update.html', source_id=source_id)
    return redirect('/login/')


@app.route('/datasource/add/')
def DataSourceAdd():
    """新增数据源"""
    if session.get('login'):
        return render_template('datasource/datasource_add.html')
    return redirect('/login/')
