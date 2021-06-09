#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__FW__'


from markdownx.fields import MarkdownxFormField
from django import forms
from zanhu.qa.models import Question, Answer


class QuestionForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())  # forms.HiddenInput() 表示隐藏

    class Meta:
        model = Question
        content = MarkdownxFormField()
        fields = ['title', 'content', 'tags', 'status']


class AnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        content = MarkdownxFormField()
        fields = ['content', ]


