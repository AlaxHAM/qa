#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.urls import path
from channels.routing import URLRouter, ProtocolTypeRouter  # ProtocolTypeRouter 通过区分协议来执行不同的处理
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from zanhu.messager.consumers import MessageConsumer
from zanhu.notifications.consumers import NotificationConsumer

# self.scope["type"] 来获取协议类型
# self.scope["url_route"]["kwargs"]["username"]  来获取websocket路由中的关键字参数
# channels routing是一个scope级别的，一个连接只能由一个consumer进行接收和处理


application = ProtocolTypeRouter({
    # "http": views   http协议的请求就交给django中的视图去处理，在channels的routing中可以不用写，默认情况下http会自动加载交给响应视图处理
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("ws/notifications/", NotificationConsumer),
                path("ws/<str:username>/", MessageConsumer),
            ])
        )
    )
})

# AuthMiddlewareStack 用于websocket的认证，集成了CookieMiddleware, SessionMiddleware，兼容了django认证处理系统
# AllowedHostsOriginValidator 用于在认证前先判断是否是允许访问的域名或IP，会自动加载django的DJANGO_ALLOWED_HOSTS中的配置来判断
# OriginValidator 的区别就是手动去配置允许的主机列表，而不是去使用django中配置的DJANGO_ALLOWED_HOSTS
# AllowedHostsOriginValidator 和 OriginValidator 的目的都是为了防止通过websocket进行的CSRF攻击

"""
OriginValidator的手动配置

application = ProtocolTypeRouter({
    "websocket": OriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path("ws/<str:username>/", MessageConsumer),
            ])
        ),["www.biadu.com","192.168.1.100",]
    )
})
"""


