#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages     # 用于做消息提示
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator     # 方法装饰器
from django.views.decorators.cache import cache_page

from django_comments.signals import comment_was_posted

from zanhu.articles.models import Articles
from zanhu.articles.forms import ArticlesForm
from zanhu.utils.utils import AuthorRequireMixin
from zanhu.notifications.views import notification_handler


class ArticlesListView(LoginRequiredMixin, ListView):
    """已发布的文章列表"""
    model = Articles
    paginate_by = 20
    context_object_name = "articles"
    template_name = "articles/article_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        """添加文章标签的上下文对象"""
        context = super(ArticlesListView, self).get_context_data()
        context["popular_tags"] = Articles.objects.get_counted_tags()
        return context

    def get_queryset(self):
        """直返回已经发布的文章,直接调用模型类已经写好的方法"""
        return Articles.objects.get_published()


class DraftsListView(ArticlesListView):
    """草稿箱文章列表"""
    def get_queryset(self):
        """返回当前用户的草稿"""
        return Articles.objects.filter(user=self.request.user).get_drafts()


@method_decorator(cache_page(60*60), name="get")   # method_decorator 的参数name指的是类的方法，这里将文章创建类的get请求方式获取的页面缓存1个小时
class ArticlesCreateView(LoginRequiredMixin, CreateView):
    """创建一篇文章"""
    model = Articles
    template_name = "articles/article_create.html"
    form_class = ArticlesForm
    msg = "您的文章已创建成功"

    def form_valid(self, form):
        """重写CreateView的form_vaild方法添加作者信息，form_vaild当表单校验通过有效时，会保存这个表单模型对象"""
        form.instance.user = self.request.user   # 给form实例对象的user字段赋值为登录用户
        return super(ArticlesCreateView, self).form_valid(form)

    def get_success_url(self):
        """创建成功跳转的页面url，并添加消息机制"""
        messages.success(self.request, message=self.msg)  # messages.success 将消息提示传递给下一次请求
        return reverse_lazy("articles:list")
        # 消息机制与信号量不同，消息机制的消息只会传递到下一次请求，再之后就不会有效；信号量则是请求的前或后做进一步处理


class ArticleDetailView(LoginRequiredMixin, DetailView):
    """文章详情"""
    model = Articles
    template_name = "articles/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return Articles.objects.select_related("user").filter(slug=self.kwargs['slug'])


class ArticleUpdateView(LoginRequiredMixin, AuthorRequireMixin, UpdateView):
    """文章编辑"""
    model = Articles
    form_class = ArticlesForm
    template_name = "articles/article_update.html"
    context_object_name = "article"
    msg = "您的文章编辑成功！"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ArticleUpdateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(request=self.request, message=self.msg)
        return reverse_lazy("articles:article", kwargs={"slug": self.get_object().slug})


@login_required
@require_http_methods(["POST"])
def notify_comment(**kwargs):
    """文章评论时通知作者"""
    actor = kwargs["request"].user
    obj = kwargs["comment"].content_object   # Comment 其实是一个通用类模型 content_object 去获取用户当前的评论
    from django_comments.models import Comment
    notification_handler(actor=actor, recipient=obj.user, verb="C", action_object=obj)


# 观察者模式 = 订阅[列表] + 通知(同步)
comment_was_posted.connect(receiver=notify_comment)
# 当用户评论了，comment_was_posted 会发出信号去执行 receiver 参数的方法
