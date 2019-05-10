#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
此模块为链表生成模块
主要为程序调用虚拟链路表示

"""


from logger import Logger
logger = Logger(__name__).Logger


class LNode(object):
	"""
	链表结点类
	"""
	
	def __init__(self, elem, next_=None):
		self.elem = elem
		self.next = next_
		

class LinkedListUnderflow(ValueError):
	"""
	链表异常类
	"""
	pass
	
	
class LList(object):
	"""
	链表实现类，普通定义上的链表
	"""
	def __init__(self):
		self._head = None
		
	def is_empty(self):
		"""
		判断链表是否为空
		"""
		return self._head is None
		
	def sort(self):
		"""
		链表元素排序类
		"""
		pass
		
	def length(self):
		"""
		求链表的长度
		"""
		p, n = self._head, 0
		while p is not None:
			n += 1
			p = p.next
		return n
		
	def rev(self):
		"""
		链表翻转
		"""
		p = None
		while self._head is not None:
			q = self._head
			self._head = q.next
			q.next = p
			p = q
			
		self._head = p
		
	def prepend(self, elem):
		"""
		从链表头部插入元素
		elem: 为要插入的元素
		"""
		self._head = LNode(elem, self._head)
		
	def pop(self):
		"""
		从链表头部删除元素
		"""
		if self._head is None:
			raise LinkedListUnderflow("in LList pop")
		
		e = self._head.elem
		self._head = self._head.next
		return e
		
	def insert(self, elem, pred=None):
		"""
		从链表任意位置插入元素
		注：该函数未完成，不可调用
		"""
		if self._head is None:
			self._head = LNode(elem)
		q = LNode(elem)
		q.next = pred.next
		pred.next = q
		
	def append(self, elem):
		"""
		在链表尾部插入元素
		elem: 要插入的元素
		"""
		if self._head is None:
			self._head = LNode(elem)
			return
		p = self._head
		# 寻找尾节点
		while p.next is not None:
			p = p.next
			
		p.next = LNode(elem)
		
	def find(self, pred):
		"""
		寻找到满足指定条件的表元素
		只返回第一个找到的元素
		"""
		p = self._head
		while p is not None:
			if pred(p.elem):
				return p.elem
			p = p.next
			
	def index(self, index_num):
		"""
		根据索引值找到对应结点的值
		索引值从0开始
		"""
		if self._head is None:
			raise LinkedListUnderflow("in LList index")
		p, n = self._head, 0
		
		if index_num > (self.length() - 1):
			raise LinkedListUnderflow("out range of the chain list in index")
			
		while p is not None:
			if index_num == n:
				return p.elem
			n += 1
			p = p.next
		
	def printall(self):
		"""
		输出该链表中的所有的元素
		"""
		p = self._head
		list_path = ''
		while p is not None:
			# print(p.elem, end=' ')
			list_path += str(p.elem) + ' '
			if p.next is not None:
				# print(", ", end= ' ')
				list_path += ", " + ' '
			p = p.next
		list_path += ' '
		logger.info(list_path)
		
	def for_each(self, proc):
		"""
		对链表中每个元素做同一操作
		proc: 一个操作函数
		"""
		p = self._head
		while p is not None:
			proc(p.elem)
			p = p.next
		
	def elements(self):
		"""
		链表生成器
		"""
		p = self._head
		while p is not None:
			yield p.elem
			p = p.next
			
	def filter(self, pred):
		"""
		寻找到所有满足指定条件的表元素
		pre: 可通过lambda函数表示
		如: lambda a: a==2 -->表示a等于2成立
		"""
		p = self._head
		while p is not None:
			if pred(p.elem):
				yield p.elem
			p = p.next
			
	
	
class LListEnd(LList):
	"""
	链表实现类
	该链表带有终结点的识别
	"""
	
	def __init__(self):
		LList.__init__(self)
		# 尾节点记忆
		self._rear = None
		
	def prepend(self, elem):
		"""
		在链表的开头插入新元素
		注：与LList的区别是，如果是初始结点，多了个尾节点的记忆
		"""
		if self._head is None:
			self._head = LNode(elem, self._head)
			self._rear = self._head
		else:
			self._head = LNode(elem, self._head)
			
	def rev(self):
		"""
		链表翻转
		"""
		p = None
		rear_change = True
		
		while self._head is not None:
			q = self._head
			self._head = q.next
			q.next = p
			p = q
			if real_change:
				self._rear = p
				rear_change = False
				
		self._head = p
		
	def append(self, elem):
		"""
		再链表的结尾插入元素
		"""
		if self._head is None:
			self._head = LNode(elem, self._head)
			self._rear = self._head
		else:
			self._rear.next = LNode(elem)
			self._rear = self._rear.next
			
	def pop_last(self):
		"""
		从链表尾部删除元素
		"""
		if self._head is None:
			raise LinkedListUnderflow("in LListEnd pop_list")
		p = self._head
		if p.next is None:
			e = p.elem
			self._head = None
			return e
		
		while p .next.next is not None:
			p = p.next
			
		e = p.next.elem
		p.next = None
		self._rear = p
		return e
		
	
		
	
