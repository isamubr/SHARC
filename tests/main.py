# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 19:23:27 2017

@author: edgar
"""

import unittest
import sys
import os

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

loader = unittest.TestLoader()
tests = loader.discover('.')
testRunner = unittest.runner.TextTestRunner()
test_results = testRunner.run(tests)

if(test_results.errors != [] or test_results.failures != []): sys.exit(1)
