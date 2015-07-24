#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: client.py
#         Desc:
#       Author: orain.xiong
#        Email: orain.xiong@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 2015-05-30 00:35:36
#      History:
#=============================================================================
'''
from celery import Celery
from celery_config import get_message_struct
from celery_config import app

app.conf.CELERY_IMPORTS = "workers"

# 依据task 名称确定走到哪个exchange上，依据路由键确定走到哪个perf_group上,
# 再依据task名称确定执行哪个task


message = get_message_struct()
message['msg_body'] = [10, 99]
message['publish_type'] = 'direct'
message['routing_key'] = 'A'
result = app.send_task('direct_add', args=(message, ), kwargs={})
print result.get()


message = get_message_struct()
message['msg_body'] = "ge.jin@woqutech.com"
message['publish_type'] = 'random'
result = app.send_task(str('random_send_email'), args=(message, ), kwargs={})
print result.get()


message = get_message_struct()
message['msg_body'] = "ge.jin@woqutech.com"
message['publish_type'] = 'broadcast'
result = app.send_task(str('all_reload'), args=(message, ), kwargs={})
print result.get()
