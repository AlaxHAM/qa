#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

import tempfile    # 用来处理临时使用的文件

from test_plus.test import TestCase
from PIL import Image
from django.test import override_settings, Client    # 用来重写settings中的配置
from django.urls import reverse
from zanhu.articles.models import Articles


class ArticleViewTest(TestCase):

    @staticmethod
    def get_temp_img():
        """创建并读取临时的图片"""
        size = (200, 200)
        color = (255, 255, 255, 0)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:   # delete=False 表示不删除临时文件
            img = Image.new("RGB", size=size, color=color)
            img.save(f, 'PNG')
        return open(f.name, 'rb')

    def setUp(self) -> None:
        """初始化操作"""
        self.test_img = self.get_temp_img()

        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")

        self.client = Client()
        self.other_client = Client()

        self.client.login(username="user01", password="password")
        self.other_client.login(username="user02", password="password")

        self.first_article = Articles.objects.create(
            title="标题1",
            content="内容1",
            # image=self.test_img,
            status="P",
            user=self.user,
        )

    def tearDown(self) -> None:
        """测试结束后，将临时文件关闭"""
        self.test_img.close()

    def test_article_list(self):
        """测试文章列表页"""
        initial_count = Articles.objects.filter(status="P").count()
        response = self.client.get(reverse("articles:list"))
        assert response.status_code == 200
        assert self.first_article in response.context["articles"]
        assert initial_count == 1

    def test_error_404(self):
        """访问不存在的文章，测试返回结果状态码是否是404"""
        response = self.client.get(reverse("articles:article", kwargs={"slug": 'no-slug'}))
        self.assertEqual(response.status_code, 404)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())    # 使用装饰器重写media的路径，让测试图片存储在临时的media文件
    def test_article_create(self):
        """测试文章发布，是否能成功跳转"""
        response = self.client.post(
            reverse("articles:write_new"),
            {"title": "标题3", "content": "内容3", "image": self.test_img, "status": "P", "tags": "test"})
        self.assertEqual(response.status_code, 302)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_draft_article(self):
        """测试草稿箱功能"""
        response = self.client.post(
            reverse("articles:write_new"),
            data={"title": "标题4", "content": "内容4", "image": self.test_img, "tags": "test", "status": "D"})
        draft_res = self.client.get(reverse("articles:drafts"))
        assert response.status_code == 302
        assert draft_res.context["articles"][0].slug == "biao-ti-4"






