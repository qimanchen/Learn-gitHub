#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.urls import path
from . import views

urlpatterns = [path('',views.index,name='index'),]
# path参数
# route -- 匹配url的准则
# view -- 当找到一个特定的视图函数就会调用
# kwargs -- 传递给目标视图函数
# name -- url别名