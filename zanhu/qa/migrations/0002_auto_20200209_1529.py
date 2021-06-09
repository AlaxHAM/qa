# Generated by Django 2.2 on 2020-02-09 07:29

from django.db import migrations
import markdownx.models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='content',
            field=markdownx.models.MarkdownxField(verbose_name='回答内容'),
        ),
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='多个标签使用,(英文)隔开', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='问题标签'),
        ),
    ]
