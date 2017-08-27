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
import sys
reload(sys)
sys.setdefaultencoding('utf8')




def get_source_list(html):
    source_list = re.findall('<div class="c" id="M_(.*?)">', html)
    print "successfully get source list."
    return source_list


def get_idlist(html):
    buseridlist = re.findall('<a class="nk" href="https://weibo.cn/(.*?)">', html)
    useridlist = []
    true_userid_list = []
    for item in buseridlist:  # 处理 特殊的用户id（如：VIP账号的ip）
        if item[1] == '/':  # 获取的id为 u/123456
            useridlist.append(item[2:])  # 处理后为 123456
        else:
            useridlist.append(item)  # id为 vipid

    for userid in useridlist:
        match = re.findall('[a-zA-Z]', userid)
        if match:  # id带英文
            true_userid = get_user_true_userid(userid=userid, headers=headers)
            true_userid_list.append(true_userid)
        else:
            true_userid_list.append(userid)
    print "successfully get idlist."
    return true_userid_list

def get_user_true_userid(userid, headers):  #vip用户的真正用户id需要进入用户主页的资料中查看
    time.sleep(6)
    userurl = 'http://weibo.cn/' + userid
    request = urllib2.Request(userurl, headers=headers)
    html = urllib2.urlopen(request).read()
    true_userid = re.findall('私信</a>&nbsp;<a href="/(.*?)/info">资料</a>', html)
    print "successfully get user true userid."
    return true_userid[0]

def get_userinfo(userid, headers):
    userurl = 'http://weibo.cn/' + userid + '/info'
    print userurl
    time.sleep(6)
    request = urllib2.Request(userurl, headers=headers)
    html = urllib2.urlopen(request).read()

    username = re.findall('昵称:(.*?)<br/>', html)
    usersex = re.findall('性别:(.*?)<br/>', html)
    userregion = re.findall('地区:(.*?)<br/>', html)
    userbri = re.findall('生日:(.*?)<br/>', html)

    if not username:            #用户url特殊，特别处理(用户加V，且主页链接中的伪id为数字）
        true_userid = get_user_true_userid(userid=userid, headers=headers)
        userurl = 'http://weibo.cn/' + true_userid + '/info'
        print "修正后的用户url:" + userurl
        id_list[id_list.index(userid)] = true_userid    #将列表中的id替换为真正的id
        time.sleep(6)
        request = urllib2.Request(userurl, headers=headers)
        html = urllib2.urlopen(request).read()
        username = re.findall('昵称:(.*?)<br/>', html)
        usersex = re.findall('性别:(.*?)<br/>', html)
        userregion = re.findall('地区:(.*?)<br/>', html)
        userbri = re.findall('生日:(.*?)<br/>', html)
    if not username:
        username.append('NONE')
    if not usersex:
        usersex.append('NONE')
    if not userregion:
        userregion.append('NONE')
    if not userbri:
        userbri.append('NONE')

    #print username[0], usersex[0], userregion[0], userbri[0]
    user_info = {'name': username[0], 'gender': usersex[0], 'region': userregion[0], 'birthdate': userbri[0]}
    print "successfully get userinfo."
    return user_info


def get_comments_text_location(url, headers, flag):     #返回包含所有内容和评论的列表（列表的第一条内容不是评论，而是微博内容）
    datas = []
    finallyurl = url + '1'
    time.sleep(6)
    request = urllib2.Request(finallyurl, headers=headers)
    html = urllib2.urlopen(request).read()

    #此部分获取微博发布地点
    if flag == 1:
        selector = etree.HTML(html)
        content = selector.xpath('//*[@id="M_"]/div[1]/span/a')
        location = unicode(content[0].xpath('string(.)'))
        if location[0] == 'h':
            location = "NONE"
    else:
        location = "NONE"


    try:
        totalpage = re.findall('<input name="mp" type="hidden" value="(.*?)" />', html)[0]
    except:
        totalpage = '1'

    print "    评论总页数：", totalpage

    for item in range(1, int(totalpage) + 1):
        if item != 1:
            finallyurl = url + str(item)
            time.sleep(6)
            request = urllib2.Request(url=finallyurl, headers=headers)
            html = urllib2.urlopen(request).read()
        print "    当前评论网页：", finallyurl
        selector = etree.HTML(html)
        content = selector.xpath('//span[@class="ctt"]')
        for it in content:
            datas.append(unicode(it.xpath('string(.)')))
    print "successfully get datas & location."
    return datas, location

def get_islocation(html):
    islocation = []
    aa = []
    bb = []
    selector = etree.HTML(html)
    b = selector.xpath('//div[@class="c"]/div[1]')
    for it in b:
        bb.append(unicode(it.xpath('string(.)')))

    a = selector.xpath('//span[@class="ctt"]')
    for it in a:
        aa.append(unicode(it.xpath('string(.)')))


    for i in range(0, 10):
        try:
            if (bb[i].split(' ​ ')[1][0] == '显'):
                islocation.append(1)
            else:
                if (aa[i].split(' ​​​ ')[1][0] == '全' and bb[1].split(' ')[2][0] == '显'):
                    islocation.append(1)
                else:
                    islocation.append(0)
        except:
            islocation.append(0)
    print "successfully get islocation."
    return islocation

def get_time(html, starttime):
    now_time = datetime.datetime.now()
    btimes = []
    times = []
    selector = etree.HTML(html)
    bbtime = selector.xpath('//span[@class="ct"]')
    for it in bbtime:
        btimes.append(unicode(it.xpath('string(.)')))
    for it in btimes:
        if '分钟' in it:      #如果发布时间为 40分钟前
            num = re.findall('\d+', it)[0]
            yes_time = now_time + datetime.timedelta(minutes=-int(num))
            yes_time = yes_time.strftime('%Y-%m-%d %H:%M')
            times.append(yes_time)
        else:
            if '今天' in it:          #如果发布时间为 今天 10:56
                rtime = starttime[0:4] + '-' + starttime[4:6] + '-' + starttime[-2:] + ' ' + it[3:8]
                times.append(rtime)
            else:                   #发布时间为 07月20日 07:53
                rtime = starttime[0:4] + '-' + starttime[4:6] + '-' + starttime[-2:] + ' ' + it[7:12]
                times.append(rtime)
    print "successfully get time."
    return times


def get_transpond_like_comment(html):
    transponds = re.findall('>转发\[(.*?)]</a>', html)
    likes = re.findall('>赞\[(.*?)\]</a>', html)
    comments = re.findall('>评论\[(.*?)\]</a>', html)
    print "successfully get transponds, likes, comments."
    return transponds, likes, comments


def download(keyword, starttime, endtime, cookievalue):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'cookie': cookievalue}

    preurl = "http://weibo.cn/search/mblog?hideSearchFrame=&keyword=" + keyword + '&advancedfilter=1&hasori=1&starttime=' + starttime + '&endtime=' + endtime + '&sort=time&page='
    data = []

    print '当前关键词为：' + keyword

    finallyurl = preurl + "1"
    time.sleep(1)
    request = urllib2.Request(finallyurl, headers=headers)
    html = urllib2.urlopen(request).read()

    try:
        totalpage = re.findall('<input name="mp" type="hidden" value="(.*?)" />', html)[0]  # 判断搜索结果是否为多页
    except:
        totalpage = '1'
    print "内容总页数：", totalpage

    for webpagenum in range(1, int(totalpage) + 1):
        try:
            print "当前微博日期为:" + starttime + "   开始爬取第" + str(webpagenum) + "个网页："
            if webpagenum != 1:
                finallyurl = preurl + str(webpagenum)
                time.sleep(2)
                request = urllib2.Request(finallyurl, headers=headers)
                html = urllib2.urlopen(request).read()
            print finallyurl

            # 获取用户信息
            userinfo_list = []
            id_list = get_idlist(html=html)
            for it in id_list:
                userinfo = get_userinfo(userid=it, headers=headers)
                userinfo_list.append(userinfo)

            # 获取每条微博的转发量、点赞数、评论数量
            transponds, likes, comments_counts = get_transpond_like_comment(html=html)

            # 获取每条微博的发布时间
            times = get_time(html=html, starttime=starttime)

            # 获取每条微博的内容、评论、地点
            islocation = get_islocation(html=html)

            source_list = get_source_list(html=html)

            for source in source_list:  # 遍历访问每一条微博
                i = source_list.index(source)

                weibourl = "http://www.weibo.cn/233/" + source  # 一个例子：https://weibo.cn/（这里什么数字都可以）/FhIa61vrm

                data, location = get_comments_text_location(url=weibourl + '?page=', headers=headers,
                                                            flag=islocation[i])
                userinfo = userinfo_list[i]
                created_time = times[i]
                u_id = id_list[i]
                transpond = transponds[i]
                like = likes[i]
                comments_count = comments_counts[i]

                try:
                    post = {
                        'source': "http://weibo.cn/" + source,
                        'weibo_id': source,
                        'location': location,  # 未完成
                        'created_at': created_time,
                        'date': jsdate,
                        'user_mentions': [],  # 未完成
                        'u_id': u_id,
                        'userinfo': userinfo,
                        'text': data[0],
                        'reposts_count': transpond,
                        'likes_count': like,
                        'comments_count': comments_count,
                        'comments': data[1:]
                    }
                    cache.insert(post)
                except:
                    print "导入数据库出错，请检查数据库是否开启"
                    exit()
                print "爬取完成"
                i += 1
        except urllib2.HTTPError:
            print "服务器拒绝访问！"
            exit()
        except:
            print "其他错误"

def startscrape(cookie, db, keyword, starttime, endtime):
    my_collection = db['SinaWeiBoData']
    download(keyword=keyword, starttime=starttime, endtime=endtime, cookievalue=cookie, cache=my_collection)
