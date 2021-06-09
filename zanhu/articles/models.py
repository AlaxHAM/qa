#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from __future__ import unicode_literals

from slugify import slugify   # 用于生成标题的拼音作为文章的url
from taggit.managers import TaggableManager   # 用于创建tag标签
from markdownx.models import MarkdownxField   # 引入markdownx的属性字段处理文章内容的预览
from markdownx.utils import markdownify       # 用来处理markdown显示的html文本

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings


@python_2_unicode_compatible
class ArticlesQueryest(models.query.QuerySet):
    """自定义queryset，提高模型类的可用性"""
    def get_published(self):
        """获取已发表的文章"""
        return self.filter(status="P").select_related("user")

    def get_drafts(self):
        """获取草稿箱中的文章"""
        return self.filter(status="D").select_related("user")

    def get_counted_tags(self):
        """获取已发表文章的文章标签, 且每一个标签数量大于0"""
        tag_dict = {}
        query_obj = self.get_published().annotate(c_tag=models.Count("tags")).filter(c_tag__gt=0)
        for obj in query_obj:
            for tag in obj.tags.names():  # .names() 返回 self.get_queryset().values_list("name", flat=True)，是一个标签的列表结果
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()   # 返回标签出现次数的元组结果


@python_2_unicode_compatible
class Articles(models.Model):
    STATUS = (("D", "Draft"), ("P", "Published"))

    title = models.CharField(max_length=255, unique=True, verbose_name="标题")
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name="author", on_delete=models.SET_NULL, verbose_name="作者")
    image = models.ImageField(upload_to="articles_pictures/%Y/%m/%d", verbose_name="文章图片")
    slug = models.SlugField(max_length=255, null=True, blank=True, verbose_name="(URL)别名")
    status = models.CharField(max_length=1, choices=STATUS, default="D", verbose_name="文章状态")
    content = MarkdownxField(verbose_name="文章内容")
    edited = models.BooleanField(default=False, verbose_name="是否可编辑")
    tags = TaggableManager(help_text="多个标签使用,(英文)隔开", verbose_name="文章标签")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    objects = ArticlesQueryest.as_manager()    # 让模型关联自定义查询集

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            """根据作者和标题生成文章在URL中的别名"""
            self.slug = slugify(self.title)
        super(Articles, self).save(*args, **kwargs)

    def get_markdown(self):
        """将markdown文本转化为html文本"""
        return markdownify(self.content)  # 将文章内容传给markdownify，返回预览的结果



