#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        recipient = self.scope["user"].username
        # news 动态发布时通知所有在线用户
        if text_data.get("key") == "additional_news":
            await self.send(text_data=json.dumps(text_data))
        # 只通知接收者，即 recipient != 动作发出者（自己对自己不提示通知）， recipient == 动作对象的作者
        if recipient != text_data.get("actor_name") and recipient == text_data.get("action_object"):
            await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        await self.channel_layer.group_discard("notifications", self.channel_name)




