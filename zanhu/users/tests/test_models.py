#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from test_plus.test import TestCase


class TestUser(TestCase):

    def setUp(self):
        """创建测试用户信息"""
        self.user = self.make_user()  # 创建 username='testuser', password='password'

    def test__str__(self):
        self.assertEqual(self.user.username.__str__(), "testuser")

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), "/users/testuser/")

    def test_get_profile_name(self):
        assert self.user.get_profile_name() == "testuser"
        self.user.nickname = "newname"
        assert self.user.get_profile_name() == "newname"



