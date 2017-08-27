#-*- coding:utf-8 -*-
import re
import urlparse
import urllib
import urllib2
import time
from datetime import datetime
import datetime
import robotparser
import Queue
import time
from lxml import etree
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from pyvirtualdisplay import Display

#获取cookie


def LoginWeibo(username, password):
    N = 0
    # display = Display(visible=0, size=(1024, 768))
    # display.start()
    driver = webdriver.Firefox()
    wait = ui.WebDriverWait(driver, 10)
    cookies_dict = {}
    # 先调用无界面浏览器PhantomJS或Firefox
    while not cookies_dict:
        if N < 20:
            url = "https://passport.sina.cn/signin/signin?entry=wapsso&vt=4&r=http%3A%2F%2Fmy.sina.cn%2F%3Fvt%3D4%26pos%3D108&amp;revalid=1"
            print u"准备登陆网站......"
            driver.get(url)
            time.sleep(2)

            try:
                user_info = driver.find_element_by_xpath("//input[@id='loginName']")
            except Exception:
                print u"用户名路径错误！"
            user_info.clear()
            user_info.send_keys(username)

            try:
                pwd_info = driver.find_element_by_xpath("//input[@id='loginPassword']")
            except Exception:
                print u"密码路径错误！"
            pwd_info.clear()
            pwd_info.send_keys(password)

            try:
                sub_info = driver.find_element_by_xpath("//a[@id='loginAction']")
            except Exception:
                print u"登陆路径错误！"
            sub_info.click()
            time.sleep(9)

            # driver.get_cookies()类型list 仅包含一个元素cookie类型dict
            cookies_dict = driver.get_cookies()
            N = N + 1
        else:
            exit(0)

    # print driver.current_url
    # print cookies_dict  # 获得cookie信息 dict存储
    # print u'输出Cookie键值对信息:'
    cookie = ''
    for item in cookies_dict:
        # print cookie
        cookie = cookie + item['name'] + '=' + item['value'] + ';'

    print u'登陆成功...'
    driver.close()      #最后启动的Firefox，先关闭
    display.stop()      #最先启动的虚拟桌面，最后关闭
    # return driver
    return cookie

