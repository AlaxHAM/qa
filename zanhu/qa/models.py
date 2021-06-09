#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'


from __future__ import unicode_literals
import uuid
from collections import Counter

from slugify import slugify
from taggit.managers import TaggableManager   # 用于创建tag标签
from markdownx.models import MarkdownxField   # 引入markdownx的属性字段处理文章内容的预览
from markdownx.utils import markdownify       # 用来处理markdown显示的html文本

from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


@python_2_unicode_compatible
class Vote(models.Model):
    """使用django中的contentType，同时关联用户对问题和回答的投票"""
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="qa_vote", on_delete=models.CASCADE, verbose_name="用户")
    value = models.BooleanField(default=True, verbose_name="赞同或反对")   # True表示赞同，False表示反对

    # GenericForeignkey 设置
    content_type = models.ForeignKey(ContentType, related_name="vote_on", on_delete=models.CASCADE)
    # 表示通过外键关联contenttype表，找到要查询对象所在的表也就是模型类
    object_id = models.CharField(max_length=255)
    # 表示通过使用contenttype表关联的表的主键找到关联记录，如果被关联表主键不是int，就需要使用CharField
    vote = GenericForeignKey('content_type', 'object_id')   # 这两个字段可以不用写，前提是要与上面写的字段一致，如果更改就需要填写

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "投票"
        verbose_name_plural = verbose_name
        unique_together = ("user", "content_type", "object_id")  # 设置联合唯一键   一个用户每次只能对一个关联对象投一次票
        # SQL索引优化
        index_together = ("content_type", "object_id")   # 联合唯一索引


@python_2_unicode_compatible
class QuestionQueryest(models.query.QuerySet):
    """自定义queryset，提高模型类的可用性"""
    def get_answered(self):
        """获取已被接受答案的问题"""
        return self.filter(has_answer=True)

    def get_unanswered(self):
        """获取没有被回答的问题"""
        return self.filter(has_answer=False)

    def get_counted_tags(self):
        """获取已发表问题的标签, 且每一个标签数量大于0"""
        tag_dict = {}
        for obj in self.all():
            for tag in obj.tags.names():  # .names() 返回 self.get_queryset().values_list("name", flat=True)，是一个标签的列表结果
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()   # 返回标签出现次数的元组结果


@python_2_unicode_compatible
class Question(models.Model):
    STATUS = (("O", "Open"), ("C", "Close"), ("D", "Draft"))
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name="q_author", on_delete=models.CASCADE,
                             verbose_name="提问者")
    title = models.CharField(max_length=255, unique=True, verbose_name="问题标题")
    slug = models.SlugField(max_length=255, null=True, blank=True, verbose_name="(URL)别名")
    status = models.CharField(max_length=1, choices=STATUS, default="O", verbose_name="问题状态")
    content = MarkdownxField(verbose_name="问题内容")
    tags = TaggableManager(help_text="多个标签使用,(英文)隔开", verbose_name="问题标签")
    has_answer = models.BooleanField(default=False, verbose_name="被采纳的回答")
    votes = GenericRelation(Vote, verbose_name="问题投票情况")  # 通过GenericRelation关联Vote模型，votes字段不是实际字段因此在数据库表中不会显示
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    objects = QuestionQueryest.as_manager()    # 让模型关联自定义查询集

    class Meta:
        verbose_name = "问题"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            """根据作者和标题生成文章在URL中的别名"""
            self.slug = slugify(self.title)
        super(Question, self).save(*args, **kwargs)

    def get_markdown(self):
        """将markdown文本转化为html文本"""
        return markdownify(self.content)  # 将内容传给markdownify，返回预览的结果

    def total_votes(self):
        """统计得票数，得票数 = 赞同数 - 反对数"""
        vote_dic = Counter(self.votes.values_list("value", flat=True))
        return vote_dic[True] - vote_dic[False]

    def get_answers(self):
        """获取所有的回答"""
        return Answer.objects.filter(question=self).select_related("user", "question")  # 参数self表示当前问题的所有回答

    def count_answer(self):
        """获取回答的数量"""
        return self.get_answers().count()

    def get_upvoters(self):
        """获取赞同的用户"""
        return [vote.user for vote in self.votes.filter(value=True).select_related("user").prefetch_related("vote")]

    def get_downvoters(self):
        """获取反对的用户"""
        return [vote.user for vote in self.votes.filter(value=False).select_related("user").prefetch_related("vote")]

    def get_accepted_answer(self):
        """获取问题被接受的回答"""
        return Answer.objects.get(question=self, is_answer=True)


@python_2_unicode_compatible
class Answer(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="a_author",
                            verbose_name="回答者", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name="问题", on_delete=models.CASCADE)
    content = MarkdownxField(verbose_name="回答内容")
    is_answer = models.BooleanField(default=False, verbose_name="回答是否被接受")
    votes = GenericRelation(Vote, verbose_name="回答投票情况")  # 通过GenericRelation关联Vote模型
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ("is_answer", "-created_at")   # 如果问题有被接受的最佳答案，优先按此字段排序，没有则按照回答时间排序
        verbose_name = "回答"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        """统计得票数，得票数 = 赞同数 - 反对数"""
        vote_dic = Counter(self.votes.values_list("value", flat=True))
        return vote_dic[True] - vote_dic[False]

    def get_upvoters(self):
        """获取赞同的用户"""
        return [vote.user for vote in self.votes.filter(value=True).select_related("user").prefetch_related("vote")]

    def get_downvoters(self):
        """获取反对的用户"""
        return [vote.user for vote in self.votes.filter(value=False).select_related("user").prefetch_related("vote")]

    def accept_answer(self):
        """接受用户回答"""
        # 查询出所有的回答，将是否被接受全部设置为False，只让当前回答被采纳接受
        answer_set = Answer.objects.filter(question=self.question)
        answer_set.update(is_answer=False)
        # 接受当前回答并保存
        self.is_answer = True
        self.save()
        # 让问题显示已有接受的回答并保存
        self.question.has_answer = True
        self.question.save()


