#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'ronglexie'
import hashlib
import re

def md5(value):
    if(isinstance(value,str)):
        value = value.encode("utf-8")
    m = hashlib.md5()
    m.update(value)
    return m.hexdigest()

# 获取数字
def extract_num(value):
    nums_match = re.match('.*(\d)+.*', value)
    if (nums_match):
        value = int(nums_match.group(1))
    else:
        value = 0
    return value