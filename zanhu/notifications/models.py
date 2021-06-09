#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from __future__ import unicode_literals
import uuid

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType  # fieldsb模块中有引入models.ContentType
# from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core import serializers

from slugify import slugify


@python_2_unicode_compatible
class NotificationQueryset(models.query.QuerySet):
    def unread(self):
        return self.filter(unread=True).select_related("actor", "recipient")

    def read(self):
        return self.filter(unread=False).select_related("actor", "recipient")

    def mark_all_as_read(self, recipient=None):   # recipient 表示登录用户 即 通知接收者
        """将通知全部标记已读"""
        qs = self.unread()
        if recipient:
            # 过滤出当前用户的所有接收通知
            qs = qs.filter(recipient=recipient)
        return qs.update(unread=False)

    def get_most_recent(self, recipient=None):
        """获取用户最近的5条通知"""
        qs = self.unread()[:5]
        if recipient:
            qs = qs.filter(recipient=recipient)[:5]
        return qs

    def serialize_latest_notifications(self, recipient: object = None) -> object:
        """序列化最近5条未读通知，来让websocket接收处理"""
        qs = self.get_most_recent(recipient)
        notification_dic = serializers.serialize("json", qs)
        # 使用的是django.core的serializers.serialize模块按照json格式序列化queryset对象
        return notification_dic


@python_2_unicode_compatible
class Notification(models.Model):
    """关联各模型类的通知模型类"""
    NOTIFICATIONS_CHOICE = (
        ('L', '赞了'),       # like
        ('C', '评论了'),     # comment
        ('F', '收藏了'),     # favour
        ('A', '回答了'),     # answer
        ('W', '接受了回答'),  # accept
        ('R', '回复了'),     # reply
        ('I', '登录'),       # login
        ('O', '退出'),       # logout
    )
    uuid_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="触发者", related_name="notify_actor", on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="接收者", related_name="notifications", on_delete=models.CASCADE)
    unread = models.BooleanField(default=True, verbose_name="未读")
    slug = models.SlugField(max_length=255, null=True, blank=True, verbose_name="(URL)别名")
    verb = models.CharField(max_length=1, choices=NOTIFICATIONS_CHOICE, verbose_name="通知类型")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    content_type = models.ForeignKey(ContentType, related_name="notify_action_object", null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    action_object = GenericForeignKey()      # 或 GenericForeignKey("content_type", "object_id")

    objects = NotificationQueryset.as_manager()

    class Meta:
        verbose_name = "通知"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        if self.action_object:
            return f'{self.actor} {self.get_verb_display()} {self.action_object}'
        return f'{self.actor} {self.get_verb_display()}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(f'{self.recipient} {self.uuid_id} {self.verb}')
        super(Notification, self).save()

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()
