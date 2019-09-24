# !/usr/bin/env python
# -*- coding:utf-8 -*-

"""
配置文件载入所有配置
"""
import json
import datetime
from flask import Flask, render_template
from flask import Markup
from flask_restplus import Api

from conn.mysqldb import MySQLdb
from scheduler.scheduler import Scheduler
from server.decorators import DictModel
from server.logger import create_logger
from server.super_config import SuperConf
from scheduler.scheduler import SchedulerConfig

config = SuperConf(path='superconf.json')

# 日志对象
log = create_logger(config, 'server')

# Flask 对象
app = Flask(__name__)
app.jinja_env.filters['json'] = lambda v: Markup(json.dumps(v))
app.secret_key = '\x1a\x8dfb#\xb9\xc8\xc3\x05\x86|\xda\x96\xff\xceo3\xf0\xa3\xb8\x8beoW'

# 调度对象
app.config.from_object(SchedulerConfig())
scheduler = Scheduler()
scheduler.init_app(app)
scheduler.start()

# Flask API 对象
api = Api(
    app,
    version='1.0.0',
    title='高并发网状调度中心 API Beta-1.0.0',
    description='高并发网状调度中心 HCNDC API Beta-1.0.0',
    ui=True
)

# 数据库连接
db = DictModel({
    'etl_db': MySQLdb(dict(config.mysql.etl))
})

# session超时时间
app.permanent_session_lifetime = datetime.timedelta(days=3)


# 跨域设置
@app.after_request
def cors(resp):
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    resp.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,HEAD')
    return resp


# flask全局异常捕获
@app.errorhandler(404)
def page_not_found(e):
    log.warn('访问了未知路径: [error: %s]' % (e,), exc_info=True)
    return render_template('exception/except.html', status_coder=404, title='资源未找到',
                           content='访问了未知路径: [error: %s]' % e)


@app.errorhandler(400)
def bad_request(e):
    log.warn('错误的请求参数: [error: %s]' % (e,), exc_info=True)
    return render_template('exception/except.html', status_coder=400, title='参数错误',
                           content='错误的请求参数: [error: %s]' % e)


@app.errorhandler(500)
def internal_server_error(e):
    log.warn('内部服务发生异常: [error: %s]' % (e,), exc_info=True)
    return render_template('exception/except.html', status_coder=500, title='服务器内部错误',
                           content='内部服务发生异常: [error: %s]' % e)


# api异常处理
@api.errorhandler(Exception)
def resource_internal_server_error(e):
    log.warn('服务发生异常: [error: %s]' % (e,), exc_info=True)
    return {'status': 500, 'msg': '失败'}, 500


@api.errorhandler(ValueError)
@api.errorhandler(TypeError)
def value_error(e):
    log.warn('服务发生异常: [error: %s]' % (e,), exc_info=True)
    return {'status': 500, 'msg': '失败'}, 500


# 非测试环境不开启API界面
if config.env.deploy != "dev":
    @api.documentation
    def disable_document():
        return api.render_root()
