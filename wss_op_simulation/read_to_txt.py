#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
此模块的目的是为了从程序中读取内容到txt文档中去

"""
from logger import Logger
logger = Logger(__name__).Logger
import os


class FileReadWrite(object):
	"""
	定义文件的读取和写入
	主要是对格式的一个定义
	"""
	
	def __init__(self, file_name, open_type):
		# 打开一个文件，读入方式为覆盖写入
		# 组建指定目录
		if 'w' not in open_type:
			dict = self.join_dict()
		else:
			dict = ''
		self.file_name = dict + file_name
		self.open_type = open_type
		self._file = open(self.file_name, self.open_type)
	
	@staticmethod
	def join_dict(spec_dict=None):
		"""
		指定数据存储的目录
		"""
		main_dict = os.getcwd()
		if spec_dict is not None:
			dict = main_dict + "\\data\\" + spec_dict + "\\"
		else:
			dict = main_dict + "\\data\\"
		return dict
		
	def __del__(self):
		"""
		防止文件再程序结束时未关闭
		"""
		Logger.info("检测到文件'{}'未关闭".format(self.file_name))
		self._file.close()
	
	def close(self):
		"""
		关闭文件
		"""
		self._file.close()
	
	def read(self):
		"""
		一次性读取文件中的全部的内容
		"""
		content = self._file.read()
		return content
		
	def readline(self):
		"""
		读取文件中的一行的内容
		返回一个列表
		会返回制表符，换行符
		"""
		contents = []
		content = self._file.readline()
		while content != '':
			contents.append(content)
			content = self._file.readline()
		return contents
		
	def readlines(self):
		"""
		读取文件的所有内容，并以列表的形式返回
		"""
		content = self._file.readlines()
		return content
		
	def write(self, content):
		"""
		写入文件
		"""
		content.encode("utf-8")
		self._file.write(content)
	
"""

# 读取
# read() 一次性读取全部内容
with open('filename.txt', 'r') as f:
	data = f.read()	# 读取文件
	print(data)
	
# readline() 读取第一行内容
with open('filename.txt', 'r') as f:
	data = f.readline()
	print(data)
	
# readlines() 读取所有的内容，并以列表的方式返回
with open('filename.txt', 'r') as f:
	data = f.readlines()	# readlines会读取到换行符，可用 strip('\n')去除
	print(data)
	
	
# 写入
# 写入时不会记录回车键
# 换行要单独写入
with open("test.txt", 'w+') as f:
	f.write('command')

"""



