# !/usr/bin/env python
# -*- coding: utf-8 -*-

from configs import app
from flask import render_template, session, redirect


@app.route('/params_index/add/')
def ParamsIndexAdd():
    """新增参数菜单"""
    if session.get('login'):
        return render_template('params_index/index_add.html')
    return redirect('/login/')
