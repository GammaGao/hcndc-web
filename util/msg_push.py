# !/usr/bin/python
# -*-coding: utf-8 -*-

import smtplib, time
from email.mime.text import MIMEText
from dingtalkchatbot.chatbot import DingtalkChatbot

from configs import log


def send_mail(alert_type, params):
    """
    发送邮件
    @alert_type: 1: 成功, 2: 失败
    @exec_id: 执行id
    @host: "smtp.exmail.qq.com"
    @port: 465
    @send_user: "baojing2@datalab.fun" / "baojing3@datalab.fun"
    @to_list: "xuexiang@tuandai.com"
    @sub: python群发邮件测试
    @content: "<a href='http://blog.csdn.net/Marksinoberg/article/details/51501377'>测试链接</a>"
    password: "UrcEP+@zNyM3vh"
    """
    exec_id = params['exec_id']
    dispatch_id = params['dispatch_id']
    dispatch_name = params['dispatch_name']
    update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(params['update_time']))
    host = params['param_host']
    port = params['param_port']
    send_user = params['param_config']
    to_list = params['send_mail']
    password = params['param_pass']
    if alert_type == 1:
        sub = '调度id: %s执行成功' % dispatch_id

    else:
        sub = '调度id: %s执行失败' % dispatch_id
    content = '''
    %s</br></br>
    调度id: %s</br>
    调度名称: %s</br>
    执行id: %s</br>
    执行时间: %s
    ''' % (sub, dispatch_id, dispatch_name, exec_id, update_time)

    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = send_user
    msg['To'] = to_list

    try:
        # 连接smtp服务器
        s = smtplib.SMTP_SSL()
        s.connect(host=host, port=port)
        s.login(send_user, password)
        s.sendmail(send_user, to_list, msg.as_string())
        s.close()
        log.info("params: %s, 发送邮件成功" % str({'exec_id': exec_id, 'alert_type': alert_type}))
    except Exception as e:
        log.error("发送邮件失败[ERROR: %s]" % e, exc_info=True)


def send_dingtalk(alert_type, params, is_at_all=False):
    """
    发送钉钉消息
    @webhook: "https://oapi.dingtalk.com/robot/send?access_token=bd92817749b11207820971bab315e0b46b59d1cf422f33e976495acf4aa89ef7"
    @msg: "发送消息"
    """
    exec_id = params['exec_id']
    dispatch_id = params['dispatch_id']
    dispatch_name = params['dispatch_name']
    update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(params['update_time']))
    webhook = params['param_config']
    if alert_type == 1:
        sub = '调度id: %s执行成功' % dispatch_id
    else:
        sub = '调度id: %s执行失败' % dispatch_id
    content = '%s\n调度id: %s\n调度名称: %s\n执行id: %s\n执行时间: %s' % (
        sub, dispatch_id, dispatch_name, exec_id, update_time
    )
    try:
        bot = DingtalkChatbot(webhook)
        bot.send_text(msg=content, is_at_all=is_at_all)
        log.info("params: %s, 发送钉钉成功" % str({'exec_id': exec_id, 'alert_type': alert_type}))
    except Exception as e:
        log.error("发送钉钉消息失败[ERROR: %s]" % e, exc_info=True)
