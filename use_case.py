#!/usr/bin/env python
# -*- coding: utf-8 -*-


import scpi
import wss
import logging


logging.basicConfig(level=logging.INFO, format='*** %(name)s - %(levelname)s - %(message)s')
Logger = logging.getLogger(__name__)


def use_case1():
	"""
	直接改变光开关的连接
	"""
	Logger.info("test function1")