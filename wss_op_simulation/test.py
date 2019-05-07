#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
该模块主要为测试其他模块使用的类
"""
from logger import Logger
logger = Logger(__name__).Logger
import logging

def test_logger():
	logger.info("test Logger")
	
	
if __name__ == "__main__":
	test_logger()
	logger.info("test")
	logging.info("test logging")
