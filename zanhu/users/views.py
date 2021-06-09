#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, UpdateView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/user_detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data()
        user = User.objects.get(username=self.request.user.username)
        # 因为在动态和评论在一个模型类中，所以动态的值是reply=False的对象总计
        context["moments_num"] = user.publisher.filter(reply=False).count()
        # 文章数只返回已发表的文章总计
        context["article_num"] = user.author.filter(status="P").count()
        # 评论数=文章和动态的评论总计，即reply=True
        # from django_comments.models import Comment
        # 这个模型类继承了 CommentAbstractModel，其中关联的user反向查询是related_name="%(class)s_comments"
        context["comment_num"] = user.publisher.filter(reply=True).count() + user.comment_comments.all().count()
        context["question_num"] = user.q_author.all().count()
        context["answer_num"] = user.q_author.all().count()

        tmp = set()
        # 统计我接收到来自不同用户的私信
        receiver_num = user.received_messages.all()
        for receiver in receiver_num:
            tmp.add(receiver)
        # 统计我给多少不同用户发了私信
        sender_num = user.send_messages.all()
        for sender in sender_num:
            tmp.add(sender)
        # 互动数 = 动态点赞数 + 问答点赞数 + 评论数 + 私信用户数(都有发送或接收到私信)
        context["interaction_num"] = user.liked_name.all().count() + user.qa_vote.all().count() \
                                     + context["comment_num"] + len(tmp)

        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """用户只能修改自己的个人信息"""
    model = User
    fields = ['nickname', 'email', 'picture', 'introduction', 'job_title', 'location',
              'personal_url', 'weibo', 'zhihu', 'github']
    template_name = "users/user_form.html"

    def get_success_url(self):
        """更新成功后跳转自己的个人页面"""
        return reverse("users:detail", kwargs={"username": self.request.user.username})
        # from django.shortcuts import HttpResponse
        # return HttpResponse("ok")

    def get_object(self, queryset=None):
        """获取需要给前端的用户对象"""
        return self.request.user

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("更新成功")
        )
        return super(UserUpdateView, self).form_valid(form)
