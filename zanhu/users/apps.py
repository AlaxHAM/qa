#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "zanhu.users"
    verbose_name = "用户"

    def ready(self):
        try:
            import zanhu.users.signals  # noqa F401
        except ImportError:
            pass
