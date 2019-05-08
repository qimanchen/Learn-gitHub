#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
此模块为链表生成模块
主要为程序调用虚拟链路表示

"""

from random import randint


class LNode(object):
	"""
	链表结点类
	"""
	
	def __init__(self, elem, next_=None):
		self.elem = elem
		self.next = next_
		

class Linked ListUnderflow(ValueError):
	"""
	链表异常类
	"""
	pass
	
