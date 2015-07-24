#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: workers.py
#         Desc: workers
#       Author: linfeng.yuan
#        Email: linfeng.yuan@woqutech.com
#     HomePage: www.woqutech.com
#      Version: 0.0.1
#   LastChange: 2015-07-09 15:42:58
#      History:
#=============================================================================
'''
#from celery import current_app
from celery_config import app
import time


class QMonitor(object):

    # 通过current_app实现 celery app 的 single instance mode
    # task参数说明：
    # http://docs.jinkan.org/docs/celery/userguide/tasks.html
    # name: task的名称在调用时用到
    # bind: 绑定的方法
    task_settings = [{"func_name": 'direct_add', "task_name": "direct_add"},
                     {"func_name": "all_reload", "task_name": "all_reload"},
                     {"func_name": "random_send_email", "task_name": "random_send_email"},
                     ]
    @classmethod
    def direct_add(cls, message):
        time.sleep(0.3)
        return message["msg_body"][0] + message["msg_body"][1]

    @classmethod
    def all_reload(cls, message):
        time.sleep(1)
        return "all config reload by %s" % message["msg_body"]

    @classmethod
    def random_send_email(cls, message):
        time.sleep(1)
        print "random sending email...{email}".format(email=message['msg_body'])
        print "you can saving a file or log a message here to verify it."


current_module = __import__(__name__)

def regist_task(cls):
    def bind_function(func_name, config={}):
        #@current_app.task(**config)
        @app.task(**config)
        def func(message):
            return getattr(cls, func_name)(message)
        return func

    for task_setting in cls.task_settings:
        function_name = task_setting["func_name"]

        config = {}
        if task_setting.get("task_name"):
            config["name"] = task_setting.get("task_name")

        setattr(current_module, function_name,
                bind_function(function_name, config))
