# !/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__FW__"

from django.views.generic import View
from django.core.exceptions import PermissionDenied


class AuthorRequireMixin(View):
    """验证操作的当前用户，用户动态删除和编辑"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.username == self.get_object().user.username:   # get_object() 获取当前调用的模型实例对象
            return super(AuthorRequireMixin, self).dispatch(request, *args, **kwargs)
        return PermissionDenied
