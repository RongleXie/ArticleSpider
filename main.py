#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'ronglexie'

from scrapy.cmdline import execute

import sys
import os

# 模拟cmdline执行scrapy crawl jobbole命令，便于代码调试
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "jobbole"])
# execute(["scrapy", "crawl", "zhihu"])
execute(["scrapy", "crawl", "lagou"])