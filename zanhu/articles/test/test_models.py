#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from test_plus.test import TestCase
from zanhu.articles.models import Articles


class ArticleModelsTest(TestCase):
    """文章模型类测试"""
    def setUp(self) -> None:
        """初始化操作"""
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")

        self.first_article = Articles.objects.create(
            title="文章标题1",
            content="内容1",
            user=self.user,
            status="P",
        )

        self.second_article = Articles.objects.create(
            title="文章标题2",
            content="内容2",
            user=self.user,
            # status="D",
        )


    def test_object_instance(self):
        """判断实例对象是否为Article的模型类"""
        assert isinstance(self.first_article, Articles)
        assert isinstance(self.second_article, Articles)

        assert isinstance(Articles.objects.get_published()[0], Articles)
        # 测试模型类自定义queryset方法 get_published = filter(status="P")


    def test_return_values(self):
        """测试返回值"""
        assert self.first_article.status == "P"
        assert self.first_article.status != "p"
        assert self.second_article.status == "D"
        assert str(self.first_article) == "文章标题1"    # 模型类的__str__方法默认返回文章的标题
        assert self.first_article in Articles.objects.get_published()
        assert Articles.objects.get_published()[0].content == "内容1"
        assert self.second_article in Articles.objects.get_drafts()


