#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from test_plus.test import TestCase
from django.urls import reverse, resolve


class UrlsTest(TestCase):
    """首页动态路由测试"""
    def test_list_reverse(self):
        self.assertEqual(reverse("news:list"), "/news/")

    def test_list_resolve(self):
        self.assertEqual(resolve("/news/").view_name, "news:list")

    def test_post_news_reverse(self):
        self.assertEqual(reverse("news:post_news"), "/news/post-news/")

    def test_post_news_resolve(self):
        self.assertEqual(resolve("/news/post-news/").view_name, "news:post_news")

    def test_delete_new_reverse(self):
        self.assertEqual(reverse("news:delete_news", kwargs={"pk": 1}), "/news/delete/1")

    def test_delete_new_resolve(self):
        self.assertEqual(resolve("/news/delete/1").view_name, "news:delete_news")

    def test_like_reverse(self):
        self.assertEqual(reverse("news:like_post"), "/news/like/")

    def test_like_resolve(self):
        self.assertEqual(resolve("/news/like/").view_name, "news:like_post")

    def test_post_comment_reverse(self):
        self.assertEqual(reverse("news:post_comment"), "/news/post-comment/")

    def test_post_comment_resolve(self):
        self.assertEqual(resolve("/news/post-comment/").view_name, "news:post_comment")

    def test_get_thread_reverse(self):
        self.assertEqual(reverse("news:get_thread"), "/news/get-thread/")

    def test_get_thread_resolve(self):
        self.assertEqual(resolve("/news/get-thread/").view_name, "news:get_thread")
