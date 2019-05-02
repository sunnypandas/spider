# -*- coding: utf-8 -*-

import os
import sys

from spider.utils.proxyutils import available_testing

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
if __name__ == '__main__':
    available_testing()