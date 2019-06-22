#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型被定义后，通过视图可以引用模型

视图根据参数检索数据，加载模板，
并使用检索到的数据呈现模板。
"""

from django.shortcuts import render
from .models import Person

def book_archive(request, year):
	"""
	视图
	"""
	book_list = Person.objects.filter(birth_year=year)
	context = {'year':year, 'book_list':book_list}
	# year_archive.html -- 模板
	return render(request, 'books/year_archive.html', context)