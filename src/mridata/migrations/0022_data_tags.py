# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-11-13 07:10
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('mridata', '0021_auto_20180805_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
