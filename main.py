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
import cookieget
from pymongo import MongoClient
import keywordscrape
import os
import platform

def get_db():
    client = MongoClient('localhost', 27017)
    db =client.weibo
    return db

def main():
    db = get_db()

    username = ''
    password = ''

    cookie = ''
    cookie = cookieget.LoginWeibo(username=username, password=password)
    keywords = ['Great+Barrier+Reef', '大堡礁', 'Cairns', '凯恩斯', 'Townsville', '汤斯维尔', 'Cooktown', '库克镇', 'Daintree', '戴恩树', 'Mission+Beach', '使命海滩', 'Rockhampton',
                'Whitsunday+Islands', '圣灵岛', 'Hamilton+Island', '汉密尔顿岛', 'Lady+Musgrave+Island', 'Whitehaven+Beach', '白天堂沙滩',
                'Airlie+Beach', '艾尔利海滩', 'Coral', '珊瑚', 'Gold+Coast', '黄金海岸', 'Magnetic+Island', '磁岛',
                'Daydream+Island', '白日梦岛', 'Lady+Elliot+Island', '埃里奥特夫人岛', 'Heron+Island', 'Green+Island', '绿岛', 'Fitzroy+Island', '费兹罗岛']

    bday = 0
    run_up_time = datetime.datetime.now()
    run_up_day = run_up_time.toordinal()


    path = os.getcwd()
    if (platform.uname()[0] == 'Windows'):
        path += '\Diary.txt'    #日记文件用于记录数据爬取的起始点，和终止点，以便下次启动程序时继续爬取。
    else:
        path += '/Diary.txt'

    if os.path.exists(path):
        print "Diary.txt exist"
        with open('Diary.txt', 'r') as f:
            bfday = f.read()
            bday = int(bfday.split(' ')[0])
            flagday = int(bfday.split(' ')[1])
            old_run_day = int(bfday.split(' ')[2])
            bday += run_up_day - old_run_day                                #将这次运行的时间与上次运行的时间差加到爬过的天数
            f.close()
    else:
        print "Diary.txt don't exist"
        flagday = run_up_time.toordinal()


    while(1):                                                                #从这里开始永久循环
        now_time = datetime.datetime.now()                                   #获取程序运行时当天的时间
        nowday = now_time.toordinal()

        updateday = nowday - flagday
        if (updateday > 1):                                                  #如果超过两天未更新新微博数据，则将更新运行时当天前两天的数据
            for i in range(1, updateday):
                update_time = now_time + datetime.timedelta(days=-i)
                updatetime = update_time.strftime('%Y%m%d')
                print "从标记点开始更新微博数据：", updatetime
                for keyword in keywords:
                    keywordscrape.startscrape(cookie=cookie, db=db, keyword=keyword, starttime=updatetime,
                                              endtime=updatetime)
            print "更新微博数据完毕！"
            flagday = nowday

        bday += 1                                                       #bady初始化为0，所以第一次运行程序时bday = 1，即从运行程序那天的前一天开始爬取数据

        with open('Diary.txt', 'w') as f:
            f.write(str(bday) + ' ' + str(flagday) + ' ' + str(run_up_day))
            f.close()

        yes_time = run_up_time + datetime.timedelta(days=-bday)
        starttime = yes_time.strftime('%Y%m%d')

        print "日期：", starttime
        for keyword in keywords:
            keywordscrape.startscrape(cookie=cookie, db=db, keyword=keyword, starttime=starttime, endtime=starttime)


if __name__ == '__main__':
    main()
