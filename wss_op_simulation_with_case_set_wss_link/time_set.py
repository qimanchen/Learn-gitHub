#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
时间分布函数设置
"""
import math
from logger import Logger
logger = Logger(__name__).Logger

# 定义相关常数
MODULE = 2147483647
A = 16807
LASTXN = 127773
UPTOMOD = -2836
RATIO = 0.46566128e-09	# 1/MODULE


def rnd32(seed):
	"""
	"""
	# 注意C++中的除法默认为整除
	# python中默认为浮点除法
	times = seed//LASTXN
	rest = seed - times * LASTXN
	prod1 = times * UPTOMOD
	prod2 = rest * A
	seed = prod1 + prod2
	if seed < 0:
		seed = seed + MODULE
	return seed
	
def uniform(a, b, seed):
	"""
	随机时间的分布
	"""
	seed = rnd32(seed)
	u = seed * RATIO
	u = a + u * (b-a)
	return u, seed
	
def negexp(mean, seed):
	"""
	"""
	seed = rnd32(seed)
	u = seed * RATIO
	return -(mean*math.log(u)), seed


def poisson(alpha, seed):
	"""
	"""
	n = 0
	pn = 0.0
	lim = pn = math.exp(-alpha)
	prob, seed = uniform(0.0, 1.0, seed)
	
	while prob > lim:
		n += 1
		pn *= alpha//n
		lim += pn
	return n, seed
	
def randint(min, max, seed):
	"""
	"""
	seed = rnd32(seed)
	temp = seed - 1.0
	temp = temp * (max-min+1.0)/(MODULE-1)
	if (int(temp) + min) > max:
		logger.info('Errore in rnd_int fuori range!! temp = {}\n'.format(temp))
	return int(temp) + min, seed
	