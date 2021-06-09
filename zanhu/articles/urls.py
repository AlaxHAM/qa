#!/sur/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'

from django.urls import path
from django.views.decorators.cache import cache_page   # 对页面进行缓存

from zanhu.articles import views

app_name = "articles"

urlpatterns = [
    path("", views.ArticlesListView.as_view(), name="list"),
    path("write-new-article/", views.ArticlesCreateView.as_view(), name="write_new"),
    path("drafts/", views.DraftsListView.as_view(), name="drafts"),
    path("<str:slug>/", cache_page(60*5)(views.ArticleDetailView.as_view()), name="article"),  # 对文章详情页缓存5分钟
    path("edit/<int:pk>", views.ArticleUpdateView.as_view(), name="edit_article"),

]


