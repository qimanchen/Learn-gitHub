#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优雅简洁的URL -- 衡量高品质的重要标准
指出什么样的URL调用什么样的视图

"""
from django.urls import path
from . import views
# 指定页面的urls
urlpatterns = [path('books/<int:year>', vies.year_archive),]