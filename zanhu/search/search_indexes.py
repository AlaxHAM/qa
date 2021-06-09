#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'


import datetime
from haystack import indexes

from zanhu.news.models import News
from zanhu.articles.models import Articles
from zanhu.qa.models import Question


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    """对Articles模型类中部分字段创建索引，该索引是Elasticsearch中的索引"""
    text = indexes.CharField(document=True, use_template=True, template_name='search/articles_text.txt')
    # template_name 的文件使用模板语法指定要创建索引的字段

    def get_model(self):
        return Articles

    def index_queryset(self, using=None):
        """Article模型类中的索引有更新时调用, 只对发布的文章（草稿箱则不用），且是在当前时间之后创建的文章进行更新"""
        return self.get_model().objects.filter(status="P", updated_at__lte=datetime.datetime.now())  # lte 表示小于等于


class NewIndex(indexes.SearchIndex, indexes.Indexable):
    """对News模型类中部分字段创建索引"""
    text = indexes.CharField(document=True, use_template=True, template_name='search/news_text.txt')

    def get_model(self):
        return News

    def index_queryset(self, using=None):
        """News模型类中的索引有更新时调用, 只对发布的动态（动态的评论不用），且是在当前时间之后创建的文章进行更新"""
        return self.get_model().objects.filter(reply=False, updated_at__lte=datetime.datetime.now())


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    """对Questions模型类中部分字段创建索引"""
    text = indexes.CharField(document=True, use_template=True, template_name='search/questions_text.txt')

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        """Quesiton模型类中的索引有更新时调用"""
        return self.get_model().objects.filter(updated_at__lte=datetime.datetime.now())

