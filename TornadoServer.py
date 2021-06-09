#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

import os
import sys
from tornado.options import options, define
from django.core.wsgi import get_wsgi_application
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi


# 服务器通过开启多个tornado端口，使用tornado的wsgi来实现django的wsgi应用，实现高并发

# 定义应用服务的目录
app_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
sys.path.append(os.path.join(app_path, "zanhu"))

define("port", default=6000, type=int, help="run on the given port")  # 定义tornado服务的默认端口


def main():
    tornado.options.parse_command_line()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    wsgi_app = tornado.wsgi.WSGIContainer(get_wsgi_application())  # 将django实现的wsgi放入tornado的wsgi容器中
    http_server = tornado.httpserver.HTTPServer(wsgi_app, xheaders=True)    # xheaders 参数可以获取客户端的ip地址
    http_server.listen(options.port)   # 监听端口
    tornado.ioloop.IOLoop.instance().start()   # 启动事件循环


if __name__ == '__main__':
    main()

