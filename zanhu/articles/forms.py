#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'


from markdownx.fields import MarkdownxFormField
from django import forms
from zanhu.articles.models import Articles


class ArticlesForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())  # forms.HiddenInput() 表示隐藏
    edited = forms.BooleanField(widget=forms.HiddenInput(), required=False, initial=False)
    # 因为模型类中设置里可编辑为False，所以初始值 initial 不需要，同时 required 表示不需要用户进行填写

    class Meta:
        model = Articles
        content = MarkdownxFormField()
        fields = ['title', 'content', 'image', 'tags', 'status', 'edited']
