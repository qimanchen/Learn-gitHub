#!/usr/bin/env python
# -*- coding: utf-8 -*-

import use_case
import logging
import threading
logging.basicConfig(level=logging.INFO, format='*** %(name)s - %(levelname)s - %(message)s')
Logger = logging.getLogger(__name__)


def test():
	Logger.info("test function2")
	use_case.use_case1()
	
	
if __name__ == "__main__":
	test()