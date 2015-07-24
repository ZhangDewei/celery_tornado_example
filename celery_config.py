#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: tasks.py
#         Desc:
#               1. 只要 celery 启动的时候没有制定 queue ,那么这个 worker 会监听所有申明的 queue, 那么task不用绑定到具体的 queue 上,只要 exchange 有这个 routes_key 的 mapping 规则即可
#               2. 只要使用非默认的 exchange,send_task 的时候需要制定 exchange + routes_key
#               3. 使用CELERY_QUEUES进行 mapping 不好理解
#               4. 映射到一个具体的方法,需要 task_name + exchange + route_key
#       Author: orain.xiong
#        Email: orain.xiong@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 2015-05-29 22:14:06
#      History:
#=============================================================================
'''

import jsonpickle
from kombu.serialization import register
from kombu import Queue, Exchange
from celery import Celery
#from celery.result import AsyncResult
#from celery import current_app
#from celery.contrib.methods import task_method

def get_message_struct():
    message = {
            "msg_body": None,
            "publish_type": None, # direct, broadcast, random
            "routing_key": None,
        }
    return message

# Encoder function
def my_dumps(obj):
    return jsonpickle.dumps(obj)

# Decoder function
def my_loads(obj):
    return jsonpickle.loads(obj)

register('myjson', my_dumps, my_loads,
         content_type='application/x-myjson',
         content_encoding='utf-8')

class MyRouter(object):

    def route_for_task(self, task, args=None, kwargs={}):
        message = args[0]
        if message['publish_type'] == 'broadcast':
            return {
                    'exchange': 'topic_exchange',
                    'routing_key': 'topic'
            }
        elif message['publish_type'] == 'random':
            return {
                    'exchange': 'topic_exchange',
                    'routing_key': 'random',
            }
        elif message['publish_type'] == 'direct':
            return {
                    'exchange': 'direct_exchange',
                    # just for test
                    'routing_key': message.get('routing_key')
            }
        return None

# configuration
# http://docs.jinkan.org/docs/celery/configuration.html#time-and-date-settings


class Config:
    CELERY_ENABLE_UTC = True
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_RESULT_BACKEND = 'amqp'
    # parameter deprecation
    broker_host = "127.0.0.1"
    broker_port = 5672
    broker_user = "qmonitor"
    broker_password = "letsg0"
    broker_vhost = "/"
    # amqp://qmonitor:**@localhost:5673//
    BROKER_URL = "{celery_result_backend}://{broker_user}:{broker_password}@{broker_host}:{broker_port}/{broker_vhost}".format\
        (celery_result_backend=CELERY_RESULT_BACKEND, broker_user=broker_user, broker_password=broker_password,
         broker_host=broker_host, broker_port=broker_port, broker_vhost=broker_vhost)
    # 默认使用的 exchange
    CELERY_DEFAULT_EXCHANGE = 'woqutech'
    CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
    CELERY_TASK_RESULT_EXPIRES = 60  # 60s
    CELERY_ACCEPT_CONTENT = ['myjson']
    CELERY_TASK_SERIALIZER = 'myjson'
    CELERY_RESULT_SERIALIZER = 'myjson'
    CELERY_QUEUE_HA_POLICY = 'all'
    CELERYD_CONCURRENCY = 50  # 并发worker数
    CELERYD_FORCE_EXECV = True    # 非常重要,有些情况下可以防止死锁
    CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker最多执行万100个任务就会被销毁,可防止内存泄露
    CELERY_CREATE_MISSING_QUEUES = True  # 某个程序中出现的队列,在broker中不存在,则立刻创建它
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_ROUTES = (MyRouter(), )
    #CELERY_IMPORTS = ("workers")


def init_queue_conf(perf_group):
    CELERY_QUEUES = (
        # 跟 perf_group binding的专属队列, 完成perf group affinity task
        Queue(
            "DIRECT_TO_%s"%perf_group,
            exchange=Exchange('direct_exchange', type='direct'),
            routing_key='%s'%perf_group,
            auto_delete=True,
            durable=True),

        # topic方式 route ,完成所有 perf 需要完成的task, 例如重读meta info,configuration file
        # 所有 perf 需要使用各自的 queue, 因为每个 worker 都要完成一遍这个 task
        Queue(
            "TOPIC_TO_%s"%perf_group,
            exchange=Exchange('topic_exchange', type='topic'),
            routing_key='topic.#',
            auto_delete=True,
            durable=True),

        # message 类型 : 被一个 worker 接收完成即可
        Queue(
            "RANDOM",
            exchange=Exchange('topic_exchange', type='topic'),
            routing_key='random.#',
            auto_delete=True,
            durable=True),
    )
    return CELERY_QUEUES

app = Celery()
app.config_from_object(Config)
