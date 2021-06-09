import os
import sys

print(os.pardir)   # ..
print(os.path.abspath(__file__))

app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)

print(app_path)    # /root/zanhu/config/..


import json
from channels.generic.websocket import AsyncWebsocketConsumer
# from haystack.signals import RealtimeSignalProcessor

class MessageConsumers(AsyncWebsocketConsumer):

    async def connect(self):
        """建立连接"""
        if self.scope["user"].is_anonymous:
            # is_anonymous 方法会去判断该用户是否经过认证
            await self.close()
        else:
            # 登录用户，则将该用户加入到 channels 的组中
            await self.channel_layer.group_add(self.scope["user"].username, self.channel_name)
            # group_add 中第一个参数是组名，第二个参数是 channel_name 随机生成的频道名
            await self.accept()
            # accept 方法就是接受 websocket 协议

    async def receive(self, text_data=None, bytes_data=None):
        """将接受的数据发送给前端"""
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        """关闭连接"""
        await self.channel_layer.group_discard(self.scope["user"].username, self.channel_name)
        # 将当前的用户从消息组中移出









