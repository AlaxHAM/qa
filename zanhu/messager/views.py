#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'


from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.template.loader import render_to_string

from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async, async_to_sync   # sync_to_async 将同步转异步， async_to_sync将异步转同步

from zanhu.messager.models import Message
from zanhu.notifications.views import notification_handler


class MessagesListView(LoginRequiredMixin, ListView):
    """消息列表页"""
    model = Message
    template_name = "messager/message_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MessagesListView, self).get_context_data()
        # 获取除当前登录用户外的所有用户，按最近登录时间降序
        context["users_list"] = get_user_model().objects.filter(is_active=True).\
            exclude(username=self.request.user.username).\
            order_by("-last_login")
        # 获取最近的一次私信互动用户
        last_conversation = Message.objects.get_most_recent_conversation(recipient=self.request.user)
        context["active"] = last_conversation.username
        return context

    def get_queryset(self):
        """获取私信最近的内容"""
        active_user = Message.objects.get_most_recent_conversation(recipient=self.request.user)
        return Message.objects.get_conversation(sender=self.request.user, recipient=active_user)


class ConversationListView(MessagesListView):
    """获取指定用户的私信内容"""
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConversationListView, self).get_context_data()
        context["active"] = self.kwargs["username"]
        # 当用户选择指定用户时，会从url中的关键字username获取被选择的用户
        return context

    def get_queryset(self):
        active_user = get_object_or_404(get_user_model(), username=self.kwargs["username"])
        # django.shortchuts.get_object_or_404  获取对象，不存在返回404，第一个参数是指定的模型类，第二个参数是查询的该模型类的参数
        return Message.objects.get_conversation(sender=self.request.user, recipient=active_user)


@login_required
@require_http_methods(["POST"])
def send_msg(request):
    """发送消息，ajax_post请求"""
    if request.is_ajax():
        sender = request.user
        recipient_user = request.POST["to"]  # 获取前端中被选择接收消息的用户名
        recipient = get_user_model().objects.get(username=recipient_user)
        message = request.POST["message"]  # 获取前端中用户发送的信息
        if len(message.strip()) != 0 and sender != recipient:
            msg = Message.objects.create(
                sender=sender,
                recipient=recipient,
                message=message,
            )

            channel_layer = get_channel_layer()   # 获取私信所在频道
            payload = {
                "type": "receive",  # 固定键值字段，receive指的是consumers中的def receive方法来发送消息
                "message": render_to_string("messager/single_message.html", {"message": msg}),     # 消息的内容
                # 为了让接受到的消息能直接在前端消息列表里渲染，使用render_to_string方法直接将消息渲染到single-message的html文件，再由此渲染消息到消息的列表中
                "sender": sender.username,  # 消息的发送者
            }
            # django的本身是同步的，而consumer中的方法又都是异步的代码，所以需要进行转换（同步的代码中必须都是同步的，反之异步的代码也必须都是异步的）
            # async_to_sync 将是将异步的方法转为同步，类似于装饰器的写法，所以async_to_sync的参数是异步的方法，而这个方法的参数则是写在async_to_sync()的后面
            async_to_sync(channel_layer.group_send)(group=recipient_user, message=payload)
            # group_send 将message消息发送到group这个组里，第一个参数是组名，第二参数是消息内容

            notification_handler(actor=sender, recipient=recipient, verb="R", key="new_message",
                                 action_object=msg.recipient)

            return render(request, 'messager/single_message.html', {'message': msg})
        return HttpResponse()


