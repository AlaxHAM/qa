#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from zanhu.notifications.models import Notification


class NotificationUnreadListView(LoginRequiredMixin, ListView):
    """未读通知消息列表"""
    model = Notification
    template_name = "notifications/notification_list.html"
    # context_object_name = "notification_list"  # 默认该属性的值就是 模型类小写 + _list  表示前端文件使用上下文对象
    # notification_list 即 get_queryset 获取的对象集的键，前端文件可以遍历或渲染这个键对应的值（queryset）

    def get_queryset(self):
        return self.request.user.notifications.unread()
        # 获取request用户对象，通过通知类接收者的一对多反向查询notifications获取所有登录用户的接收通知


@login_required
def get_latest_notifications(request):
    """获取最近的5条通知消息"""
    notifications_queryset = request.user.notifications.get_most_recent()
    return render(request, "notifications/most_recent.html", {"notifications": notifications_queryset})


@login_required
def mark_all_read(request):
    """标记所有通知为已读"""
    request.user.notifications.mark_all_as_read()

    # 如果用户是在其他功能页中跳转的，需要获取当前请求的url，然后当用户操作完成使用当前url跳转回去
    redirect_url = request.GET.get("next")

    messages.add_message(request, messages.SUCCESS, f"所有通知已标记已读")

    if redirect_url:
        return redirect(redirect_url)
    return redirect("notifications:unread")


@login_required
def mark_read(request, slug):
    """根据slug来对单条的通知标记已读"""
    notification = get_object_or_404(Notification, slug=slug)
    # 如果直接使用 Notification.objects.get(slug=slug) 需要加上try..except..else来处理可能出现的异常情况
    # get_object_or_404相比之下，会更加便捷，如果get不到会直接返回404表示异常
    notification.mark_as_read()
    messages.add_message(request, messages.SUCCESS, f"已将通知{notification}标为已读")
    redirect_url = request.GET.get("next")
    if redirect_url:
        return redirect(redirect_url)
    return redirect("notifications:unread")


def notification_handler(actor, recipient, verb, action_object, **kwargs):
    """
    通知处理器函数
    :param actor: request.user 登录用户对象，动作发起者
    :param recipient: user instance 接收者用户实例，可以是一个或多个接收者
    :param verb: str 通知的类别
    :param action_object: instance 动作对象实例
    :param kwargs: key, id_value
    :return: None
    """

    key = kwargs.get("key", "notification")
    id_value = kwargs.get("id_value", None)

    # 记录通知内容，保存至数据库
    Notification.objects.create(
        actor=actor,
        recipient=recipient,
        verb=verb,
        action_object=action_object,
    )

    if key == "new_message":
        action_object = action_object.username
    else:
        action_object = action_object.user.username

    channel_layer = get_channel_layer()
    payload = {
        "type": "receive",
        "key": key,   # key参数的目的是当websocket发送消息后，前端会接收这个key，通过判断这个值来触发请求
        "actor_name": actor.username,
        "action_object": action_object,
        "id_value": id_value,
    }
    async_to_sync(channel_layer.group_send)("notifications", payload)












