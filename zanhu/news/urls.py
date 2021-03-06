#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.urls import path
from zanhu.news import views

app_name = "news"

urlpatterns = [
    path("", views.NewsListView.as_view(), name="list"),
    path("post-news/", views.post_new, name='post_news'),
    path("delete/<str:pk>", views.NewsDeleteView.as_view(), name='delete_news'),
    path("like/", views.like, name='like_post'),
    path("post-comment/", views.post_comment, name="post_comment"),
    path("get-thread/", views.get_thread, name="get_thread"),
    path("update-interactions/", views.update_interactions, name="update_interactions/"),
]
