#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
django - description
"""

# 设计模型 Model
# django可以通过对象关系映射器
from django.db import models

class book(models.Model):
	name = models.CharField(max_length=100)
	pub_date = models.DateField()
	
# 使用models.py来描述数据表 -- 模型
# 可以通过简单的python代码来实现数据库相关的功能

