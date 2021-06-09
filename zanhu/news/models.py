#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from __future__ import unicode_literals

import uuid
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from zanhu.users.models import User
from zanhu.notifications.views import notification_handler


@python_2_unicode_compatible
class News(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             # models.SET_NULL 当父表被删除，子表置空，即如果用户被删除，则将用户设置为空，但不影响该用户已发布的的评论
                             related_name="publisher", verbose_name="用户")
    parent = models.ForeignKey(to="self", blank=True, null=True, on_delete=models.CASCADE,
                               related_name="thread", verbose_name="评论自关联")
    content = models.TextField(verbose_name="动态内容")
    liked = models.ManyToManyField(to=User, related_name="liked_name", verbose_name="点赞用户")
    # 注意：多对多的字段，设置 null=true, blank=true 是无效的
    reply = models.BooleanField(default=False, verbose_name="是否为评论")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "首页"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return self.content

    def save(self, *args, **kwargs):
        """重写save，当用户发布一个动态，在websocket监听的组中，所有用户都会收到通知，获取当前的发布动态"""

        super(News, self).save(*args, **kwargs)
        if self.reply is False:
            # 判断当前保存的对象是否是评论，是动态的话，则将动态消息加入到动态组中
            channel_layer = get_channel_layer()
            payload = {
                "type": "receive",
                "key": "additional_news",
                "actor_name": self.user.username,
            }
            async_to_sync(channel_layer.group_send)("notifications", payload)


    def switch_like(self, user):
        """点赞或取消"""
        if user in self.liked.all():   # 判断当前用户是不是在当前动态点赞的用户集合中 liked.all() 获取的是对应点赞的所有用户 User.objects.all()
            self.liked.remove(user)
        else:
            self.liked.add(user)
            # 通知楼主，给自己点赞时不通知
            if user.username != self.user.username:
                notification_handler(actor=user, recipient=self.user, verb="L", action_object=self,
                                     id_value=str(self.uuid_id), key="social_update")

    def get_parent(self):
        """获取上一级的评论记录，没有则为本身"""
        if self.parent:
            return self.parent
        else:
            return self

    def reply_this(self, user, text):
        """评论回复动态"""
        parent = self.get_parent()
        News.objects.create(user=user, content=text, reply=True, parent=parent)
        if user.username != self.user.username:
            notification_handler(user, parent.user, verb="R", action_object=parent, id_value=str(parent.uuid_id),
                                 key="social_update")

    def get_thread(self):
        """关联当前评论的所有评论记录"""
        parent = self.get_parent()
        return parent.thread.all()

    def comment_count(self):
        """评论数"""
        return self.get_thread().count()

    def count_likers(self):
        """点赞数"""
        return self.liked.count()

    def get_likers(self):
        """获取所有点赞用户"""
        return self.liked.all()
