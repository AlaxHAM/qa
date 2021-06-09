#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from __future__ import unicode_literals

import uuid
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


@python_2_unicode_compatible
class MessageQueryset(models.query.QuerySet):
    def get_conversation(self, sender, recipient):
        """获取用户间的私信会话"""
        a2b = self.filter(sender=sender, recipient=recipient).select_related("sender", "recipient")  # 获取A发送给B的消息查询集
        b2a = self.filter(sender=recipient, recipient=sender).select_related("sender", "recipient")  # 获取B发送给A的消息查询集
        return a2b.union(b2a).order_by("created_at")

    def get_most_recent_conversation(self, recipient):   # recipient表示的是登录用户（接收者）
        """获取最近一次的私信互动用户，即登录用户作为接受者，判断最后一条消息是自己发出还是发送者发出"""
        try:
            qs_sent = self.filter(sender=recipient)    # 获取登录用户发出的消息
            qs_received = self.filter(recipient=recipient)  # 获取登录用户接收的消息
            qs = qs_sent.union(qs_received).latest("created_at")
            # latest按照发送时间获取最近的消息  使用latest必须要在模型类的元类中定义ordering
            if qs.sender == recipient:
                # 如果登录用户有发送消息，就返回消息的接收者
                return qs.recipient
            else:
                # 反之，返回发送者
                return qs.sender
        except self.model.DoesNotExist:
            # 如果模型实例不存在，则返回当前用户
            return get_user_model().objects.get(username=recipient.username)


@python_2_unicode_compatible
class Message(models.Model):
    """用户私信"""
    uuid_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="发送者", related_name="send_messages", null=True, blank=True, on_delete=models.SET_NULL)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="接收者", related_name="received_messages", null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField(verbose_name="私信内容", null=True, blank=True)
    unread = models.BooleanField(default=True, verbose_name="消息是否已读")  # 默认为true表示消息未读
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="发送时间")
    objects = MessageQueryset.as_manager()

    class Meta:
        verbose_name = "私信"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return self.message

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()
