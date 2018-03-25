#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'ronglexie'
import hashlib

def md5(value):
    if(isinstance(value,str)):
        value = value.encode("utf-8")
    m = hashlib.md5()
    m.update(value)
    return m.hexdigest()