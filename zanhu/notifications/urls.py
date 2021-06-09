#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.urls import path
from zanhu.notifications import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationUnreadListView.as_view(), name="unread"),
    path("latest-notifications/", views.get_latest_notifications, name="latest_notifications"),
    path("mark-all-as-read/", views.mark_all_read, name="mark_all_read"),
    path("mark-as-read/<str:slug>", views.mark_read, name="mark_as_read"),
]
