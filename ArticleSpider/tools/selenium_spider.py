#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@version: 3.6
@author: ronglexie
@license: Apache Licence 
@contact: ronglexie@gmail.com
@site: http://www.ronglexie.top
@software: PyCharm
@file: selenium_spider.py
@time: 2018/3/31 18:57
"""

import os
from selenium import webdriver
from scrapy.selector import Selector
import time


def selenium_spider():
    chrome_opt = webdriver.ChromeOptions()
    # 设备浏览器不加载图片
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_opt.add_experimental_option("prefs", prefs)

    chrome_driver_path = os.path.abspath(os.path.dirname(__file__)) + r'\chromedriver.exe'

    browser = webdriver.Chrome(executable_path=chrome_driver_path, chrome_options=chrome_opt)

    # 完成知乎模拟登录
    browser.get("https://www.zhihu.com/signin")
    # selector = Selector(text=browser.page_source)
    # 输入用户名和密码
    browser.find_element_by_css_selector(".SignFlow-accountInput input[name='username']").send_keys("username")
    browser.find_element_by_css_selector(".SignFlowInput .Input-wrapper input[name='password']").send_keys("password")
    # 点击登录按钮
    browser.find_element_by_css_selector(".SignFlow-submitButton").click()

    # 完成微博模拟登录
    browser.get("https://weibo.com/")
    time.sleep(15)
    # selector = Selector(text=browser.page_source)
    # 输入用户名和密码
    browser.find_element_by_css_selector("#loginname").send_keys("loginname")
    browser.find_element_by_css_selector(".password input[name='password']").send_keys("password")
    # 点击登录按钮
    browser.find_element_by_css_selector(".info_list.login_btn a[node-type='submitBtn']").click()
    time.sleep(5)
    # 执行JS代码  滚动屏幕
    browser.execute_script(
        "window.scrollTo(0,document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    time.sleep(10)
    browser.close()

    # phantomjs,无界面浏览器，多进程情况下phantomjs性能会严重下降
    phantomjs_driver_path = os.path.abspath(os.path.dirname(__file__)) + r'\phantomjs.exe'

    phantomjs_browser = webdriver.PhantomJS(executable_path=phantomjs_driver_path)

    # 完成知乎模拟登录
    phantomjs_browser.get("https://www.zhihu.com/signin")

    selector = Selector(text=phantomjs_browser.page_source)
    # 获取所有链接
    selector.css("a")


if __name__ == '__main__':
    selenium_spider()