#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: celery_non_block.py
#         Desc: 
#       Author: linfeng.yuan
#        Email: linfeng.yuan@woqutech.com
#     HomePage: www.woqutech.com
#      Version: 0.0.1
#   LastChange: 2015-07-20 13:31:41
#      History:
#=============================================================================
'''


import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import tornado.httpclient
import workers
from tornado_settings import access_log, app_log, gen_log


def get_message_struct():
    message = {
        "msg_body": None,
        "publish_type": None,  # direct, broadcast, random
        "routing_key": None,
    }
    return message


class BasicRequestHandler(tornado.web.RequestHandler):

    def check_token(self):
        keyring = 'feed8cbf7b6427edb33fd5e9a53c7b3c'
        if keyring != self.request.headers.get('X-Auth-Token', None):
            app_log.warning("in log: X-Auth-Token error")
            raise tornado.web.HTTPError(403)
            self.finish()

    def fix_uri(self):
        uri = self.request.uri
        if (len(uri) > 1 and uri[-1] == '/'):
            self.request.uri = uri[:-1]
            gen_log.info("in log: fix uri...")
        elif not uri:
            self.request.uri = '/'

    def check_license(self):
        uri = self.request.uri
        if uri.split('/')[1] not in ["metainfo", "security"]:
            # 检查license是否到期
            #if True:
            if False:
                access_log.warning("in log: invalid license!")
                raise tornado.web.HTTPError(403)
                #self.write("invalid license ...\n")
                self.finish()

    def prepare(self):
        """
        prepare is called when the request headers have been read instead of after
        the entire body has been read.
        """
        self.fix_uri()
        self.check_license()


class WorkerHanler(BasicRequestHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, **params):
        args = self.get_arguments("args[]")
        task = params["worker"]
        print args

        message = get_message_struct()
        args1 = int(args[0])
        args2 = int(args[1])
        message['msg_body'] = [args1, args2]
        message['publish_type'] = 'direct'
        message['routing_key'] = 'A'
        # apply_async means none blocking
        response = yield tornado.gen.Task(getattr(workers, task).apply_async, args=[message])
        self.write("After I sleep 15s, get result %s\n" % response.result)
        self.finish()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, worker):
        args1 = self.get_argument("args1", 0)
        args2 = self.get_argument("args2", 0)

        message = get_message_struct()
        message['msg_body'] = [int(args1), int(args2)]
        message['publish_type'] = 'direct'
        message['routing_key'] = 'A'
        print "get curl..."
        # apply_async means none blocking
        response = yield tornado.gen.Task(getattr(workers, worker).apply_async, args=[message])
        self.write("After I sleep 15s, get result %s\n" % response.result)
        self.finish()


class JustNowHandler(BasicRequestHandler):

    def get(self):
        self.write("i hope just now see you\n")


def main():
    import tcelery
    from tornado.options import define, options, parse_command_line
    tcelery.setup_nonblocking_producer()
    define("port", default=8000, help="run on the given port", type=int)
    options.parse_command_line()
    app = tornado.web.Application(
            handlers = [('/do_job/(?P<worker>.*)/.*', WorkerHanler),
                        ('/justnow', JustNowHandler),
                        ],
            debug = True
            )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
