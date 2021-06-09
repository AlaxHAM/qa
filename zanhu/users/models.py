#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible   # 让程序在Python2.x环境下，能够处理Python3的unicode字符
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

@python_2_unicode_compatible
class User(AbstractUser):
    """自定义用户模型"""
    nickname = models.CharField(null=True, blank=True, max_length=255, verbose_name="昵称")
    job_title = models.CharField(max_length=50, null=True, blank=True, verbose_name="职称")
    introduction = models.TextField(null=True, blank=True, verbose_name="个人简介")
    picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True, verbose_name="头像")
    location = models.CharField(max_length=50, null=True, blank=True, verbose_name="城市")
    personal_url = models.URLField(max_length=255, null=True, blank=True, verbose_name="个人链接")
    weibo = models.URLField(max_length=255, null=True, blank=True, verbose_name="微博链接")
    zhihu = models.URLField(max_length=255, null=True, blank=True, verbose_name="知乎链接")
    github = models.URLField(max_length=255, null=True, blank=True, verbose_name="Github链接")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 更改信息不回变动这个时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")      # 每一次更改都会获取当时的时间

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name   # 使用中文 让单复数名字都是一样的

    def __str__(self):
        """更改实例对象的返回形式"""
        return self.username   # self.username 是 AbstractUser 类中已存在的唯一键

    def get_absolute_url(self):
        """返回用户详情页的url路径   通过self。username参数指定每一个详情页的url"""
        return reverse("users:detail", kwargs={"username": self.username})

    def get_profile_name(self):
        """返回用户名字   如果昵称存在则返回昵称"""
        if self.nickname:
            return self.nickname
        return self.username


