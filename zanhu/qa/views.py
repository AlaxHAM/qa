#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


from zanhu.qa.models import Question, Answer
from zanhu.qa.forms import QuestionForm, AnswerForm
from zanhu.notifications.views import notification_handler
from zanhu.utils.utils import AuthorRequireMixin



class QuestionListView(LoginRequiredMixin, ListView):
    """所有问题页"""
    model = Question
    queryset = Question.objects.select_related('user')
    paginate_by = 10
    context_object_name = "questions"
    template_name = "qa/question_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(QuestionListView, self).get_context_data()
        context["popular_tags"] = Question.objects.get_counted_tags()  # 获取标签和次数
        context["active"] = "all"
        return context


class AnsweredListView(QuestionListView):
    """已被采纳回答的问题页"""

    def get_queryset(self):
        return Question.objects.get_answered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AnsweredListView, self).get_context_data()
        context["active"] = "answered"
        return context


class UnAnsweredListView(QuestionListView):
    """没有被采纳回答的问题页"""

    def get_queryset(self):
        return Question.objects.get_unanswered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UnAnsweredListView, self).get_context_data()
        context["active"] = "unanswered"
        return context


# @method_decorator(cache_page(60*60), name="get")
class CreateQuestionView(LoginRequiredMixin, CreateView):
    """用户发布问题"""
    form_class = QuestionForm
    template_name = "qa/question_form.html"
    msg = "问题已提交！"

    def form_valid(self, form):
        # print("登录用户--------------------------------------------------------", self.request.user.username)
        form.instance.user = self.request.user
        return super(CreateQuestionView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.msg)
        return reverse_lazy("qa:all_q")


class DetailQuestionView(LoginRequiredMixin, DetailView):
    """问题详情页"""
    model = Question
    context_object_name = "question"
    template_name = "qa/question_detail.html"

    def get_queryset(self):
        return Question.objects.select_related("user").filter(pk=self.kwargs["pk"])


class UpDateAnswerView(LoginRequiredMixin, UpdateView):
    model = Answer
    form_class = AnswerForm
    template_name = "qa/answer_update_form.html"
    pk_url_kwarg = 'uuid'
    msg = "您的文章编辑成功！"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UpDateAnswerView, self).form_valid(form)

    def get_success_url(self):
        messages.success(request=self.request, message=self.msg)
        return reverse_lazy("qa:question_detail", kwargs={"pk": self.request.POST.get("question_id")})


@method_decorator(cache_page(60*60), name="get")
class CreateAnswerView(LoginRequiredMixin, CreateView):
    """用户回答问题"""
    model = Answer
    fields = ["content", ]
    template_name = "qa/answer_form.html"
    msg = "您的回答已提交！"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.question_id = self.kwargs["question_id"]
        return super(CreateAnswerView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.msg)
        return reverse_lazy("qa:question_detail", kwargs={"pk": self.kwargs["question_id"]})


@login_required
@require_http_methods(["POST"])
def question_vote(request):
    """给问题投票，ajax_post请求"""
    if request.is_ajax():
        question_id = request.POST["question"]
        value = True if request.POST["value"] == "U" else False  # 前端文件中 "U"表示赞同   "D"表示反对
        question = Question.objects.get(pk=question_id)
        users = question.votes.values_list("user", flat=True)  # 获取当前问题赞同与反对所有投票用户
        if request.user.pk in users and (question.votes.get(user=request.user).value == value):
            # 判断当前用户是否在赞或踩的所有用户集中，且当前用户操作的value与数据库中保存的之前value相同，说明用户要进行的是赞或踩的取消操作
            question.votes.get(user=request.user).delete()
        else:
            # 反之，如果用户不存在users中，或value的操作值与上一次的值不同，说明用户要进行 由赞到踩 或 由踩到赞 的操作
            question.votes.update_or_create(user=request.user, defaults={"value": value})

    """
        1. 用户首次进行，赞或踩操作
            if request.user.pk not in users:
                # question.votes.create(user=request.user, value=value)
                question.votes.update_or_create(user=request.user, defaults={"value": value})
            
        2. 用户已经赞过，要进行取消或是直接进行踩操作
            elif question.votes.get(user=request.user).value:
                if value:
                    question.votes.get(user=request.user).delete()
                else:
                    # question.votes.update(user=request.user, value=value)
                    question.votes.update_or_create(user=request.user, defaults={"value": value})
                    
        2. 用户已经踩过，要进行取消或是直接进行赞操作
            else:
                if not value:
                    question.votes.get(user=request.user).delete()
                else:
                    # question.votes.update(user=request.user, value=value)
                    question.votes.update_or_create(user=request.user, defaults={"value": value})
            
    """

    return JsonResponse({"votes": question.total_votes()})


@login_required
@require_http_methods(["POST"])
def answer_vote(request):
    """给回答投票，ajax_post请求"""
    if request.is_ajax():
        answer_id = request.POST["answer"]
        value = True if request.POST["value"] == "U" else False  # 前端文件中 "U"表示赞同   "D"表示反对
        answer = Answer.objects.get(uuid=answer_id)
        users = answer.votes.values_list("user", flat=True)  # 获取当前问题赞同与反对所有投票用户
        if request.user.pk in users and (answer.votes.get(user=request.user).value == value):
            # 判断当前用户是否在赞或踩的所有用户集中，且当前用户操作的value与数据库中保存的之前value相同，说明用户要进行的是赞或踩的取消操作
            answer.votes.get(user=request.user).delete()
        else:
            # 反之，如果用户不存在users中，或value的操作值与上一次的值不同，说明用户要进行 由赞到踩 或 由踩到赞 的操作
            answer.votes.update_or_create(user=request.user, defaults={"value": value})

    return JsonResponse({"votes": answer.total_votes()})


@login_required
@require_http_methods(["POST"])
def accept_answer(request):
    """用户接受回答，ajax_post请求"""
    if request.is_ajax():
        answer_id = request.POST["answer"]
        answer = Answer.objects.get(uuid=answer_id)
        # 接受回答之前，校验用户信息，确认是当前登录用户进行操作
        if answer.question.user.username == request.user.username:
            answer.accept_answer()
        else:
            raise PermissionDenied()
    # 使用通知器，将接受回答消息通知作者
        notification_handler(actor=request.user, recipient=answer.user, verb="W",
                             action_object=answer)
    return JsonResponse({"status": "true"})




