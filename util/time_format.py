# !/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import time
from datetime import datetime
from datetime import timedelta


def seconds_format(seconds):
    """秒数转化"""
    day = 24 * 60 * 60
    hour = 60 * 60
    minute = 60
    if seconds < 60:
        return "%d秒" % math.ceil(seconds)
    elif seconds > day:
        days = divmod(seconds, day)
        return "%d天 %s" % (int(days[0]), seconds_format(days[1]))
    elif seconds > hour:
        hours = divmod(seconds, hour)
        return '%d小时 %s' % (int(hours[0]), seconds_format(hours[1]))
    else:
        minutes = divmod(seconds, minute)
        return "%d分钟 %d秒" % (int(minutes[0]), math.ceil(minutes[1]))


def date_add(date_str, days_count=1, date_format='%Y-%m-%d'):
    """增加天数"""
    date_list = time.strptime(date_str, date_format)
    y, m, d = date_list[:3]
    delta = timedelta(days=days_count)
    date_result = datetime(y, m, d) + delta
    date_result = date_result.strftime(date_format)
    return date_result
