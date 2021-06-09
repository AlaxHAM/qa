#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.test import Client
from test_plus.test import TestCase
from django.urls import reverse
from zanhu.news.models import News


class NewsViewsTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()        # 创建客户端浏览器对象
        self.other_client = Client()

        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")
        self.client.login(username="user01", password="password")   # 在客户端对象使用login登录
        self.other_client.login(username="user02", password="password")

        self.first_news = News.objects.create(user=self.user, content="第一条动态")
        self.second_news = News.objects.create(user=self.user, content="第二条动态")
        self.third_news = News.objects.create(user=self.other_user, reply=True, content="第一条动态的评论", parent=self.first_news)

    def test_news_list(self):
        """测试动态列表首页功能"""
        response = self.client.get(reverse("news:list"))
        assert response.status_code == 200
        assert self.first_news in response.context["news_list"]
        assert self.second_news in response.context["news_list"]
        assert self.third_news not in response.context["news_list"]
        # news_list 是视图中的 context_object_name 使用过的上下文对象名，就是传递给html用于渲染的对象

    def test_delete_news(self):
        """测试删除动态"""
        initial_count = News.objects.count()
        response = self.client.post(reverse("news:delete_news", kwargs={"pk": self.second_news.pk}))
        assert response.status_code == 302   # 删除后url自动跳转列表页，所以状态码是302重定向
        assert News.objects.count() == initial_count - 1

    def test_post_news(self):
        """测试动态发布"""
        initial_count = News.objects.count()
        response = self.client.post(
            reverse("news:post_news"),
            {"post": "测试视图发布动态"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"  # 在请求头中加入表示发送的是ajax请求
        )
        assert response.status_code == 200
        assert News.objects.count() == initial_count + 1

    def test_like_news(self):
        """测试点赞"""
        response = self.client.post(     # 让user01给自己的动态点赞
            reverse("news:like_post"),
            {"news": self.first_news.pk},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert self.first_news.count_likers() == 1
        assert self.user in self.first_news.get_likers()   # get_likers()获取点赞的所有用户
        assert response.json()["likes"] == 1   # 后端使用Jsonresponse传的likes的键给前端渲染，这里的 response 的 json 方法用来对返回的 json 对象进行反序列化

    def test_get_thread(self):
        """测试动态的评论的获取"""
        response = self.other_client.get(
            reverse("news:get_thread"),
            {"news": self.first_news.pk},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        print("response:", response.json())
        assert response.status_code == 200
        assert response.json()["uuid"] == str(self.first_news.pk)
        assert "第一条动态" in response.json()["news"]
        assert "第一条动态的评论" in response.json()["thread"]

    def test_post_comment(self):
        """测试动态的评论发表"""
        response = self.other_client.post(
            reverse("news:post_comment"),
            {
                "reply": "user02的评论",
                "parent": self.first_news.uuid_id
             },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code == 200
        assert response.json()["comments"] == 2

