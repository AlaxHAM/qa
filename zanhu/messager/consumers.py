#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessageConsumer(AsyncWebsocketConsumer):
    """处理私信应用中websocket请求，使用异步方式"""
    async def connect(self):            # async 表示异步方式处理
        """判断用户状态，并加入到频道组"""
        if self.scope["user"].is_anonymous:   # 判断当前用户是否是匿名用户
            # 是匿名用户，表示未登录，直接拒绝连接
            await self.close()          # 使用异步方式时，调用的方法需要加 await
        else:
            # 反之，将被选择私信的用户加入到组中 即 group_add 的第一个参数组名
            # self.scope["user"].username表示当前的登录用户，以当前用户名作为监听频道的组名
            # 当登录用户选择其他用户进行私信时，被选择用户将加到以登录用户名作为组名的组中
            # 不同用户之间私信用channel_name来区分，也就是以登录用户名为组名的其他频道
            await self.channel_layer.group_add(self.scope["user"].username, self.channel_name)
            # group_add的第一个参数是组名以被选择的用户作为接收者，将其名字作为组名，channel_name方法会随机生成一个唯一的频道名字
            await self.accept()  # 接收连接

    async def receive(self, text_data=None, bytes_data=None):
        """接收私信"""
        # print("______text_data______", text_data)
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        """离开聊天组"""
        await self.channel_layer.group_discard(self.scope["user"].username, self.channel_name)
        # 将用户移除创建的频道组



