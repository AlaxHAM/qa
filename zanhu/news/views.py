#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DeleteView
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from django.urls import reverse_lazy

from zanhu.news.models import News
from zanhu.utils.utils import AuthorRequireMixin


class NewsListView(LoginRequiredMixin, ListView):
    """首页动态"""
    model = News
    # queryset = News.ordering.all()      # queryset参数可以对返回的对象做简单的过滤处理   默认返回对象就是模型类.all()
    paginate_by = 20    # 每页显示20条数据   url会有 ?page= 显示当前页
    # page_kwarg = "p"    # 修改分页的关键字
    template_name = "news/news_list.html"   # 默认template_name就是模型类名 + _list.html
    context_object_name = "news_list"       # 传给前端处理的对象名    默认也是 模型类名 + _list
    # ordering = ("-created_at", )             # 单个字段排序可以直接使用字符串   多个字段则需要使用元组的方式

    def get_queryset(self):
        """自定义返回对象集合"""
        return News.objects.filter(reply=False).select_related("user", "parent")    # 只返回动态集合对象  排除所有的评论回复集合对象

    # def get_paginate_by(self, queryset):
    #     """自定义分页处理"""
    #     pass
    #
    # def get_ordering(self):
    #     """自定义排序处理"""
    #     pass
    #
    # def get_context_data(self, *, object_list=None, **kwargs):
    #     """添加额外的上下文，给前端处理增加新的对象"""
    #     context = super().get_context_data()
    #     context["views"] = 100
    #     return context


class NewsDeleteView(LoginRequiredMixin, AuthorRequireMixin, DeleteView):
    """动态删除"""
    model = News
    template_name = "news/news_confirm_delete.html"
    # slug_url_kwarg = "slug"  # 通过url传入要删除对象的主键id  默认值是 slug
    # pk_url_kwarg = "pk"  # 通过url传入要删除对象的主键id  默认值是 pk
    success_url = reverse_lazy("news:list")
    # reverse_lazy 会在urlConf文件加载完成之后才会执行
    # django url文件的加载是要在所有文件完成之后才会加载，所以使用reverse_lazy  直接使用reverse会抛出异常


@login_required
@require_http_methods(["POST"])
def post_new(request):
    """ajax_post请求提交发表内容"""
    if request.is_ajax():
        post = request.POST["post"].strip()
        if post:
            info = News.objects.create(user=request.user, content=post)
            return render(request, "news/news_single.html", {"news": info})
        else:
            return HttpResponseBadRequest("请输入你要发表的内容！")  # HttpResponseBadRequest 后端会抛出400代码的错误


@login_required
@require_http_methods(["POST"])
def like(request):
    """点赞，ajax_post请求"""
    if request.is_ajax():
        news_id = request.POST["news"]
        news = News.objects.get(pk=news_id)
        # 取消或添加赞
        news.switch_like(request.user)
        # 返回赞的数量
        return JsonResponse({"likes": news.count_likers()})


@login_required
@require_http_methods(["GET"])
def get_thread(request):
    """返回动态的评论，ajax_get请求"""
    if request.is_ajax():
        news_id = request.GET["news"]
        news = News.objects.select_related("user").get(pk=news_id)
        news_html = render_to_string("news/news_single.html", {"news": news})   # 没有评论的时候
        thread_html = render_to_string("news/news_thread.html", {"thread": news.get_thread()})   # 有评论的时候
        # render_to_string()  加载模板并将数据进行渲染，最后以字符串的形式返回html文档
        return JsonResponse({"uuid": news_id, "news": news_html, "thread": thread_html})


@login_required
@require_http_methods(["POST"])
def post_comment(request):
    """用户发表评论，ajax_posy请求"""
    if request.is_ajax():
        reply_content = request.POST["reply"].strip()
        parent_id = request.POST["parent"]
        parent = News.objects.get(pk=parent_id)
        if reply_content:
            parent.reply_this(request.user, reply_content)
            return JsonResponse({"comments": parent.comment_count()})
        else:
            return HttpResponseBadRequest("回复内容不能为空！")


@login_required
@require_http_methods(["POST"])
def update_interactions(request):
    """更新互动信息"""
    if request.is_ajax():
        data_point = request.POST["id_value"]
        news = News.objects.get(pk=data_point)
        return JsonResponse({"likes": news.count_likers(), "comments": news.comment_count()})

