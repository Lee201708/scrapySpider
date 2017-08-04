'''
* 作者：Lee
* 创建：2017-06-29
* 功能：抓取百度热词榜热词
'''
# -*- coding: utf-8 -*-
# from scrapy_redis.spiders import RedisSpider
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.exceptions import CloseSpider
# import urllib
# from urllib.parse import unquote
# from urllib.parse import quote
# import urllib.request
import re
# import urllib.request
import urllib
from urllib.parse import unquote
from ScrapyWorm.items import BaiduHotWordItem

'''热词爬虫'''
'''直接从网页中抓取热词'''
class HotWord(CrawlSpider):
    name = "HotWordSpider"
    custom_settings =  {
        'ITEM_PIPELINES':{
            'ScrapyWorm.pipelines.DuplicatesPipeline_HotWord' : 250,
            # 'ScrapyWorm.pipelines.ScrapywormPipeline' : 250,
            # 'ScrapyWorm.pipelines.JsonWritePipeline': 300,
            'ScrapyWorm.pipelines.HotWordInsertMongoDBPipeline':350
        }
    }

    '''返回类别对应的热词URL'''
    def ReturnHotWordUrl(self, num):
        url = 'http://top.baidu.com/clip?b=' + num + '&hd_h_info=1&line=20&hd_border=1&hd_searches=1&hd_search=1&hd_trend=1&hd_meshline=1&hd_h=1&col=1'
        return url

    def start_requests(self):
        url = 'http://top.baidu.com/add?fr=topbuzz_b1'
        yield Request(url,callback=self.parse,dont_filter=True)

    ##########获取所有类型热词的网页###############
    def parse(self, response):
        selector = Selector(response)
        dropdownList = selector.xpath('.//select[@id="textSelect"]')
        typeNum = dropdownList.xpath('option/@value').extract()
        # typeName = dropdownList.xpath('option/text()').extract()
        # for i in range(0,1):
        for i in range(0,len(typeNum)):
            # name = typeName[i]
            num = typeNum[i]
            hotwordUrl = self.ReturnHotWordUrl(num)
            yield Request(url=hotwordUrl, callback=self.parse_getHotword,dont_filter=True)
    ############爬取热词类型对应的热词页面##############
    def parse_getHotword(self,response):
        #词源，返回热词的类型
        responseUrl = response.url
        hotwordType = re.findall('http://top\.baidu\.com/clip\?b=(\d+)&hd_h_info=1&line=20&hd_border=1&hd_searches=1&hd_search=1&hd_trend=1&hd_meshline=1&hd_h=1&col=1',responseUrl)[0]
        selector = Selector(response)
        item = BaiduHotWordItem()
        body = selector.xpath('//body').extract()[0]
        wordLists = re.findall('var BD_DATA=(.*?)var boardid',body,re.S)
        if wordLists !=[]:
            wordList = wordLists[0]
        else:
            wordList = []
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("未检索到关键字，请检查提取关键字列表的正则表达式")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        words = re.findall('"title":"(.*?)",',wordList,re.S)
        if words !=[]:
            for word in words:
                hotword = word.encode('utf8').decode('unicode-escape')
                item['HotWord'] = hotword
                item['HotWordType'] = hotwordType
                item['BDHotWordLink'] = self.BDFirstPageUrl(keyword=hotword,tp=hotwordType)
                # item['WXHotWordLink'] = self.WXFirstPageUrl(hotword)
                yield item
        else:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print("未检索到关键字，请检查列表中提取关键字的正则表达式")
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


    '''返回热词对应第一页的URL'''
    #百度
    url_prefix = "http://news.baidu.com"
    def BDFirstPageUrl(self, keyword,tp):
        # word = quote(keyword)
        '''词源'''
        words = {
            "word": keyword
            }

        params = {
            # "rsv_spt": "1",
            # "rsv_iqid": "0xf04064290000bb44",
            # "issp": "1",
            # "f": "8",
            # "rsv_bp": "0",
            # "rsv_idx": "2",
            # "ie": "utf-8",
            "tn": "news",
            "ct": "1",
            "from": "news",
            "cl": "2",
            "rn": "20"
            # "tp": tp

            # ###被百度检测到为HTTP劫持，搜索结果页的链接中，“异常”展现了tn数字后缀。例如在百度首页进行搜索时，
            # 展现的结果页地址链接为：http://www.baidu.com/s?&wd=hao123&tn=92078526_hao_pg（正常情况下应该是http://www.baidu.com/s?&wd=hao123）
            # "rsv_enter": "1",
            # "rsv_sug3": "7",
            # "rsv_sug1": "2",
            # "rsv_sug7": "100"
        }
        word = urllib.parse.urlencode(words)
        params = urllib.parse.urlencode(params)
        add_s = ''.join([self.url_prefix, "/ns"])
        BDFirstPageUrl = "?".join([add_s, word])
        BDFirstPageUrl = '&'.join([BDFirstPageUrl,params])
        return BDFirstPageUrl

    #微信
    url_header = "http://weixin.sogou.com"
    def WXFirstPageUrl(self,keyword):
        params = {
            'type': '2',
            'query': keyword,
            'ie': 'utf8',
            's_from': 'input',
            '_sug_': 'n',
            '_sug_type_': ''
        }
        param = urllib.parse.urlencode(params)
        WXFirstPageUrl = '/weixin?'.join([self.url_header, param])
        return WXFirstPageUrl
