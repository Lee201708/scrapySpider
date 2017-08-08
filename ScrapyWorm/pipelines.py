'''
* 作者：Lee
* 创建：2017-06-29
* 功能：处理Spider抓取到的数据
        InsertMongoDBPipeline       保存数据到MongoDB
        DuplicatesPipeline_HotWord  热词去重
        DropItemPipeline            过滤抓取的数据。当某些字段为空时，丢弃对应的item
        JsonWritePipeline           保存数据到Json。抓取数据过程中，每日一个json文件，同时绑定空闲信号，当程序处于空闲状态，即主动关闭json文件，保存数据。
        HbasePipeline               保存数据到Hbase
'''

# -*- coding: utf-8 -*-
import json
from scrapy import log
from scrapy.exceptions import DropItem
from scrapy.exceptions import CloseSpider
from redis import Redis
from redis import StrictRedis
from scrapy.utils.project import get_project_settings
import time
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import hashlib
from ScrapyWorm.items import TigerItem
from ScrapyWorm.hbasemodel import *
# from scrapy.conf import settings
import pymongo


# now = time.strftime("%Y%m%d")
setting = get_project_settings()
HOST = setting.get('REDIS_HOST')
PORT = setting.get('REDIS_PORT')
# DB = setting.get('REDIS_DB')
r = Redis(host=HOST, port=PORT)


class ScrapywormPipeline(object):
    def process_item(self, item, spider):
        return item

#去重复,   lpush url
class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['Title'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['Title'])
            return item

class DuplicatesPipeline_HotWord(object):

    def open_spider(self,spider):
        self.count = 0              #热词总数
        self.insertCount = 0        #成功插入的热词数
        self.dupeConut = 0          #重复的热词数

    def process_item(self, item, spider):
        hotword = item['HotWord']
        self.count += 1
        if r.sadd('HotWord:dupefilter',hotword):
            self.insertCount += 1
            print('插入成功！')
            r.lpush('BDMedia:urls',item['BDHotWordLink'])
            # r.lpush('wxNews:urls')
            return item
        else:
            print('插入失败！')
            self.dupeConut += 1
            raise DropItem("Duplicate item found: %s" % item)


    def close_spider(self,spider):
        print('本次运行共有 %d 条热词' % self.count)
        print('成功插入 %d 条热词' % self.insertCount)
        print('有 %d 条重复' % self.dupeConut)
        if self.insertCount < 10:
            with open('IncreaseTime.txt','w') as IT:
                word = 'True'
                IT.write(word)
                IT.close()
        else:
            with open('IncreaseTime.txt', 'w') as IT:
                word = 'False'
                IT.write(word)
                IT.close()
        self.count = 0
        self.dupeConut = 0
        self.insertCount = 0


#丢弃没有标题和正文的  Item

class DropItemPipeline(object):
    def process_item(self,item,spider):
        if isinstance(item,TigerItem):
            title = item['Title']
            content = item['Content']
            if title == "" or content == "":
                raise DropItem("Item have nothing useful!")
        return item

class JsonWritePipeline(object):

    def __init__(self):
        dispatcher.connect(self.spider_idle, signals.spider_idle)
        self.now = time.strftime("%Y%m%d")
        # self.opened = True

    def open_spider(self, spider):
        self.opened = True
        self.file = open('json/'+spider.name+self.now+'.json', 'a+', encoding='utf-8')
        print('json file is open!')

    def process_item(self, item, spider):
        # title = item['Title']
        # if title =="None" or title=="":
        #     raise DropItem("没有标题")
        now_T = time.strftime("%Y%m%d")
        if self.now != now_T :
            self.now = now_T
            if self.opened:
                self.file.close()
                self.opened = False
        if not self.opened:
            self.file = open('json/' + spider.name + self.now + '.json', 'a+', encoding='utf-8')
            print('json file is open again!')
            self.opened = True
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_idle(self):
        if self.opened:
            time.sleep(3)
            self.opened = False
            self.file.close()
            print('json file is closed!')
        else:
            pass

    def spider_closed(self):
        if self.opened:
            self.file.close()
        else:
            pass

class HbasePipeline(object):
    def __init__(self):
        self.HB = HBASE()
    def process_item(self,item,spider):
        title = item['Title']
        if title =="None" or title=="":
            raise DropItem("没有标题")
        news = {}
        for i in item:
            newKey =  "cf:"+i
            news[newKey] = item[i]
        self.HB.saveDict(news)
        # print(news)
        # print("存储到hbase")
            # print('pipeline输出:',newKey,news[newKey])

        return item

    # def process_item(self,item,spider):
    #     print("item初始类型：",type(item))
    #     item_B = dict(item)
    #     print("转化后item类型：",type(item_B))
    #     print(item_B)
    #     # getDict(item_B)
    #     return  item

# 热词插入到mongodb
class HotWordInsertMongoDBPipeline(object):
    def __init__(self):
        HOST = setting.get('MONGODB_HOST')
        PORT = setting.get('MONGODB_PORT')
        DBNAME = setting.get('MONGODB_DBNAME')
        MONGODB_DOCNAME1 = setting.get('MONGODB_DOCNAME1')
        client = pymongo.MongoClient(host=HOST,port=PORT)
        tdb = client[DBNAME]
        self.post = tdb[MONGODB_DOCNAME1]

    def process_item(self,item,spider):
        hotwordInfo = dict(item)
        if self.post.insert(hotwordInfo):
            print('存储成功！')
            return item
        return item

#新闻插入到mongodb
class NewsInsertMongoDBPipeline(object):
    def __init__(self):
        HOST = setting.get('MONGODB_HOST')
        PORT = setting.get('MONGODB_PORT')
        DBNAME = setting.get('MONGODB_DBNAME')
        MONGODB_DOCNAME2 = setting.get('MONGODB_DOCNAME2')
        client = pymongo.MongoClient(host=HOST,port=PORT)
        tdb = client[DBNAME]
        # self.post = tdb[setting['MONGODB_DOCNAME']]
        self.post = tdb[MONGODB_DOCNAME2]

    def process_item(self,item,spider):
        data = item['Pubtime']
        dataarray = time.strptime(data,"%Y-%m-%d")
        datastamp = int(time.mktime(dataarray))
        item['Pubtime'] = datastamp
        NewsInfo = dict(item)
        if self.post.insert(NewsInfo):
            print('存储成功！')
            return item

        return item

