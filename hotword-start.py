# -*- coding: utf-8 -*-

import time
import datetime
import subprocess
from ScrapyWorm import public_variable
import logging

class Start():
    waitTime = 7200
    minwaittime = 1600
    maxwaittime = 18000
    logging.basicConfig(filename='logs/HotWordSpiderlogger.log', level=logging.INFO)
    def get_value(self):
        with open('IncreaseTime.txt','r') as IT:
            ToIncreaseTime = IT.read()
            return ToIncreaseTime

    def m(self):
        logging.info(time.strftime("%Y-%m-%d %H:%M:%S")+'启动HotWordSpider')
        logging.info('重复启动爬虫的时间间隔为：'+str(self.waitTime/3600))
        # print("现在正在执行爬虫",time.time())
        child = subprocess.Popen("scrapy crawl HotWordSpider",shell=True)
        #在Linux运行时，需要加上 shell=True
        # child = subprocess.Popen("scrapy crawl HotWordSpider",shell=True)
        # print('等待结束，正在请求网页',time.time())
        child.wait()
        logging.info(time.strftime("%Y-%m-%d %H:%M:%S")+'抓取完毕')
        print(time.strftime('%Y-%m-%d %H:%M:%S'), '运行结束')
        ToIncreaseTime = self.get_value()
        if ToIncreaseTime == 'True':
            if self.waitTime >= self.maxwaittime:
                self.waitTime = self.maxwaittime
            else:
                self.waitTime += 1800
        elif self.waitTime <= self.minwaittime :
            self.waitTime = self.minwaittime
        else:
            self.waitTime -= 1800
        logging.info('将等待'+str(self.waitTime/3600)+'小时,即在'+(datetime.datetime.now()+datetime.timedelta(seconds=self.waitTime)).strftime('%Y-%m-%d %H:%M:%S')+'再次启动。')
        logging.info('----------------------------------------------------------------------------------------------------------------')
        logging.info('----------------------------------------------------------------------------------------------------------------')
        logging.info('----------------------------------------------------------------------------------------------------------------')
        print('将等待',self.waitTime/3600,'小时,即在',(datetime.datetime.now()+datetime.timedelta(seconds=self.waitTime)).strftime('%Y-%m-%d %H:%M:%S')+'再次启动。')
        time.sleep(self.waitTime)

if __name__ == '__main__':
    start = Start()
    while True:
        start.m()
