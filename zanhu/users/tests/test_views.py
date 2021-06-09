#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.test import RequestFactory
from test_plus.test import TestCase
from users.views import UserUpdateView


class BaseUserTestCase(TestCase):
    """测试基类"""
    def setUp(self):
        self.factory = RequestFactory()
        self.user = self.make_user()


class TestUserUpdateView(BaseUserTestCase):
    def setUp(self):
        super(TestUserUpdateView, self).setUp()
        self.view = UserUpdateView()

        request = self.factory.get("/fake-url")  # 使用工厂直接创建request请求
        request.user = self.user                 # 给创建的request请求加上用户信息
        self.view.request = request              # 将request交给视图处理
        # 这个request请求不经过wsgi，url和中间件，而是直接把请求发给视图做测试

    def test_get_success_url(self):
        self.assertEqual(self.view.get_success_url(), "/users/testuser/")

    def test_get_object(self):
        self.assertEqual(self.view.get_object(), self.user)

