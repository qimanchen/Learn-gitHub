#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志信息格式设置
创建日期：2019/05/07
author: QimanChen
"""

import logging
import sys
import inspect


def get_current_function_name():
	"""
	获取当前运行函数的函数名
	模块名
	"""
	return inspect.stack()[1][3]

class Logger(object):
	"""
	logger
	日志信息格式设置类
	调用格式
	logger = Logger(function_name).Logger
	"""
	def __init__(self, function_name):
	
		logging.basicConfig(level=logging.INFO, format='*** %(name)s - %(levelname)s - %(message)s')
		self.Logger = logging.getLogger(function_name)


# logging.basicConfig(level=logging.INFO, format='*** %(name)s - %(levelname)s - %(message)s')
# Logger = logging.getLogger(get_current_function_name())


# 显示被调用函数的文件名 -- 完整路径
# sys._getframe().f_code.co_filename