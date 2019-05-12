#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
该模块主要为测试其他模块使用的类
"""
from logger import Logger
logger = Logger(__name__).Logger
import logging
from chain_list import LList, LListEnd
from read_to_txt import FileReadWrite

def test_logger():
    logger.info("test Logger")
    
def test_chain_list(): 
    llist = LList()
    llistend = LListEnd()
    
if __name__ == "__main__":
    read_file = FileReadWrite('test_write.txt', 'r')
    
    

            
            
