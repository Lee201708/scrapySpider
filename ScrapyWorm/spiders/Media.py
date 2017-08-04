'''
* 作者：Lee
* 创建：2017-06-29
* 功能：提取网页数据
        深度爬取
'''


# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.spiders import RedisCrawlSpider
# from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
import re
from scrapy.linkextractors import LinkExtractor
# from scrapy.linkextractors.sgml import SgmlLinkExtractor
# from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule
import time
import json
from ScrapyWorm.items import TigerItem
from urllib.parse import unquote
from urllib.parse import unquote

from scrapy import Item,Field

'''爬虫3'''
'''通用爬虫，获取页面的标题，正文，图片'''
class Media(RedisCrawlSpider):
    name = "MediaSpider"

    custom_settings = {
        'ITEM_PIPELINES' : {
            # 'ScrapyWorm.pipelines.HbasePipeline': 100,
            'ScrapyWorm.pipelines.DropItemPipeline': 100,
            # 'ScrapyWorm.pipelines.JsonWritePipeline' : 200,
            'ScrapyWorm.pipelines.NewsInsertMongoDBPipeline': 200,
        }
    }

    redis_key = 'BDMedia:urls'

    #导入规则
    def __init__(self,*args, **kwargs):
        rule1 = [
            # 联合早报
            Rule(
                LinkExtractor(
                    allow=("http://www.zaobao.com/\S+/story\d+-\d+"),
                ),
                callback="parse_LHZB",
                follow=True,
            ),
            # 中国新闻网
            Rule(
                LinkExtractor(
                    allow=("http://www.chinanews.com/\w+/\d+/\d+-\d+/\d+.shtml"),
                ),
                callback="parse_ZGXWW",
                follow=True,
            ),
            #中国新闻网-图集
            Rule(
                LinkExtractor(
                    allow=("http://www.chinanews.com/tp/hd2011/\d+/\d+-\d+/\d+.shtml"),
                ),
                callback="parse_ZGXWW_Pic",
                follow=True,
            ),
            #广州日报大洋网
            Rule(
                LinkExtractor(
                    allow=("http://news.dayoo.com/\w+/\d+/\d+/"),
                    deny=("http://news.dayoo.com/about/")
                ),
                callback="parse_DYW",
                follow=True
            ),
            #人民网
            Rule(
                LinkExtractor(
                    allow=("http://\w+.people.com.cn/n1/\d+/\d+/"),
                    deny=("http://cpc.people.com.cn/|http://tv.people.com.cn/")
                ),
                callback="parse_RMW",
                follow=True
            ),
            # 中华网
            Rule(
                LinkExtractor(
                    allow=("http://\w+.china.com/\S+/\d+.html")
                ),
                callback="parse_ZHW",
                follow=True
            ),
            # 东方头条
            Rule(
                LinkExtractor(
                    allow=("http://mini.eastday.com/a/\\d+.html"),
                    deny=("http://mini.eastday.com/a/\\d+-\\d+.html")
                ),
                callback="parse_DFTT",
                follow=True
            ),
            #澎湃新闻
            Rule(
                LinkExtractor(
                    allow=("http://www.thepaper.cn/newsDetail_forward_\d+"),
                    deny=("http://www.thepaper.cn/asktopic_detail_\d+")
                ),
                callback="parse_PPXW",
                follow=True
            ),
            #参考消息
            Rule(
                LinkExtractor(
                    allow=("http://www.cankaoxiaoxi.com/\S+/\d+.shtml"),
                    deny=("http://www.cankaoxiaoxi.com/photo/")
                ),
                callback="parse_CKXX",
                follow=True,
            ),
            # 网易新闻
            Rule(
                LinkExtractor(
                    allow=("http://\w+.163.com/\d+/\S+"),
                    deny = ("http://renjian.163.com|http://product.auto.163.com/")
                ),
                callback="parse_WY",
                follow=True
            ),
            #搜狐新闻
            Rule(
                LinkExtractor(
                    allow=("http://\w+.sohu.com/a/\S+|http://\w+.sohu.com/\d{8}/\S+"),
                    deny=("http://\S*auto.sohu.com|http://tv.sohu.com/")
                ),
                callback="parse_SHXW",
                follow=True
            ),
            #搜狐汽车
            Rule(
                LinkExtractor(
                    allow=("http://\S*auto.sohu.com"),
                    deny=("http://db.auto.sohu.com/")
                ),
                callback="parse_SHQC",
                follow=True
            ),
            #大众网
            Rule(
                LinkExtractor(
                    allow=("http://\w+.dzwww.com/\S+/\d\d\d\d\d\d/\S+.htm"),
                    deny=("http://dv.dzwww.com/\S+|http://www.dzwww.com/fieldofvision/|http://zibo.dzwww.com/|http://laiwu.dzwww.com/|http://bbs.dzwww.com/|http://yantai.dzwww.com/ytwh/xdsj/|http://club.dzwww.com/")
                ),
                callback="parse_DZW",
                follow=True
            ),
            # 新华网
            Rule(
                LinkExtractor(
                    allow=("http://news.xinhuanet.com/\w+/\d\d\d\d-\d\d/\d\d/\S+.htm"),
                    deny=("http://news.xinhuanet.com/video/\d\d\d\d-\d\d/\d\d/\S+.htm")
                ),
                callback="parse_XHW",
                follow=True
            ),
            # 中国青年网
            Rule(
                LinkExtractor(
                    allow=("http://\\w+.youth.cn/\\S*/\\d+/\\S+.htm")
                ),
                callback="parse_ZGQNW",
                follow=True
            ),
            # 腾讯谷雨
            Rule(
                LinkExtractor(
                    allow=("http://gy.qq.com/original/\S+.html"),
                ),
                callback="parse_TXGY",
                follow=True
            ),
            #腾讯通用
            Rule(
                LinkExtractor(
                    allow=("http://\S+.qq.com/a/\d{8}/\d+.htm"),
                    deny=("https://v.qq.com/\S+|http://gy.qq.com/")
                ),
                callback="parse_TXTY",
                follow=True
            ),
            # 环球网
            Rule(
                LinkExtractor(
                    allow=("http://\w+.huanqiu.com/(\S+)/\d\d\d\d-\d\d/(\S+)"),
                    deny=("http://\w+.huanqiu.com/p(\S+)|http://\w+.huanqiu.com/gt(\S+)|http://photo.huanqiu.com/(\S+)")
                ),
                callback="parse_HQW",
                follow=True
            ),
            # 环球图集
            Rule(
                LinkExtractor(
                    allow=("http://\w+.huanqiu.com/p(\S+)|http://\w+.huanqiu.com/gt(\S+)|http://photo.huanqiu.com/(\S+)")
                ),
                callback="parse_HQTJ",
                follow=True
            ),
            # 凤凰网
            Rule(
                LinkExtractor(
                    allow=("http://(\\S*).ifeng.com/a/"),
                    deny=("http://gentie.ifeng.com/|https://imall.ifeng.com/")
                ),
                callback="parse_FHW",
                follow=True
            ),
            # 新浪专栏
            Rule(
                LinkExtractor(
                    allow=("http://(\w+).sina.com.cn/zl\S*/\d\d\d\d-\d\d-\d\d/\S+")
                ),
                callback="parse_XLZL",
                follow=True
            ),
            # 新浪财经
            Rule(
                LinkExtractor(
                    allow=("http://finance.sina.com.cn/\S+/\d\d\d\d-\d\d-\d\d/\S+")
                ),
                callback="parse_XLCJ",
                follow=True
            ),
            # 新浪军事
            Rule(
                LinkExtractor(
                    allow=("http://mil.sina.com.cn/\S+/\d\d\d\d-\d\d-\d\d/\S+")
                ),
                callback="parse_XLJS",
                follow=True
            ),
            #新浪博客
            Rule(
                LinkExtractor(
                    allow=("http://blog.sina.com.cn/s/blog_\S*"),
                ),
                callback="parse_XLBK",
                follow=True
            ),
            # 新浪通用
            Rule(
                LinkExtractor(
                    allow=("http://(\w+).sina.com.cn/\S+/\d\d\d\d-\d\d-\d\d/\S+"),
                    deny=("http://video.sina.com.cn/\S*")
                ),
                callback="parse_XLTY",
                follow=True
            )
        ]
        # 深度爬取用
        file = open("noRule.json", 'r', encoding='utf-8')
        for i in file:
            s = json.loads(i)
            rule1.append(
                Rule(
                    LinkExtractor(allow=(s["allow"]), deny=(s["deny"]))
                )
            )
        #必须变为元组
        self.rules = tuple(rule1)
        super(Media, self).__init__(*args, **kwargs)



    def parse_command(self, response):
        # print(response.url)
        # print("请注意添加本网站的rule")
        pass

    '''广州日报大洋网'''
    def parse_DYW(self,response):
        Fr = "广州日报大洋网"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = "".join(selector.xpath("body/div[@class='dy-layout']/div[@class='dy-bd']//div[@class='dy-article']/div[@class='article-hd']/h1/text()").extract()).strip()
        pubtime_A = "".join(selector.xpath("body/div[@class='dy-layout']/div[@class='dy-bd']//div[@class='dy-article']/div[@class='article-hd']//span[@class='time']/text()").extract()).strip()
        pubtime = re.findall("(\d\d\d\d-\d\d-\d\d)",pubtime_A)
        articalsAncestor = "".join(selector.xpath("body/div[@class='dy-layout']/div[@class='dy-bd']//div[@class='dy-article']/div[@class='article-hd']//span[@class='source']/text()").extract()).strip()[3:]
        content = "".join(selector.xpath("body/div[@class='dy-layout']/div[@class='dy-bd']//div[@class='dy-article']/div[@class='content']//p//text()").extract()).strip()
        img = "\n".join(selector.xpath("body/div[@class='dy-layout']/div[@class='dy-bd']//div[@class='dy-article']/div[@class='content']//img/@src").extract()).strip()
        # print(url)
        # print(title)
        # print(pubtime)
        # print(articalsAncestor)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['ArticalAncestor'] = articalsAncestor
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item
        pass

    '''中国新闻网'''
    def parse_ZGXWW(self,response):
        Fr = "中国新闻网"
        url= response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@id='con']//div[@class='con_left']/div[@class='content']/h1/text()").extract()).strip()
        pubtime_Ancestor = ''.join(selector.xpath("body/div[@id='con']//div[@class='con_left']/div[@class='content']/div[@class='left-time']/div[@class='left-t']/text()").extract()).strip()
        pubtime = ''.join(re.findall("(\d{4}年\d{2}月\d{2}日)\d{2}:\d{2}.*",pubtime_Ancestor,re.S)).strip().replace(r'年','-').replace(r'月','-').replace(r'日','')
        content = ''.join(selector.xpath("body/div[@id='con']//div[@class='con_left']/div[@class='content']/div[@class='left_zw']/p/text()").extract()).strip()
        img = '\n'.join(selector.xpath("body/div[@id='con']//div[@class='con_left']/div[@class='content']/div[@class='left_zw']//img/@src").extract()).strip()
        # print(Fr)
        # print(url)
        # print(title)
        # print(pubtime)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item
    '''中国新闻网——图集'''
    def parse_ZGXWW_Pic(self,response):
        Fr = "中国新闻网"
        url= response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body//div[@id='mian']/div[@class='playNav']/i[@class='title']/text()").extract()).strip()
        pubtime_A = ''.join(selector.xpath("body//div[@id='mian']/div[@id='cont_show']/div[@class='zxians']/div[contains(text(),'发布时间')]/text()").extract()).strip()
        pubtime = ''.join(re.findall("发布时间：(\d\d\d\d-\d\d-\d\d)",pubtime_A)).strip()
        content = ''.join(selector.xpath("body//div[@id='mian']/div[@id='cont_show']/div[@class='zxians']/div[@class='t3']/text()").extract()).strip()
        img = '\n'.join(selector.xpath("body//div[@class='zxians']//div[@id='mian2']/div[@class='t4_2']/div[@id='scrool_div']//img/@src|body//div[@id='mian']/div[@class='playNav']/i[last()]/div[last()]/a/@href").extract()).strip()
        # print(Fr)
        # print(url)
        # print(title)
        # print(pubtime)
        # print(content)
        # print('图片',img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

        pass

    '''联合早报'''
    def parse_LHZB(self,response):
        Fr = "联合早报"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@id='CommonWealth']//div[@class='row content-main-wrapper']/div[@id='Milk']//div[@class='body-content']/h1/text()").extract())
        pubtime_A = ''.join(selector.xpath("body/div[@id='CommonWealth']//div[@class='row content-main-wrapper']/div[@id='Milk']//div[@class='body-content']/aside[@class='trackme']/span[@class='datestamp']/text()").extract())
        pubtime_B = re.findall(".*?(\d+)年(\d+)月(\d+)日.*?",pubtime_A)
        pubtime = ""
        if pubtime_B: pubtime = '-'.join(pubtime_B[0])
        author = ''.join(selector.xpath("body/div[@id='CommonWealth']//div[@class='row content-main-wrapper']/div[@id='Milk']//div[@class='body-content']/aside[@class='trackme']/span[@class='contributor meta-byline']/a/text()").extract())
        articalsAncestor = ''.join(selector.xpath("body/div[@id='CommonWealth']//div[@class='row content-main-wrapper']/div[@id='Milk']//div[@class='body-content']/aside[@class='trackme']/span[last()]/span[last()]/a/text()").extract())
        content = ''.join(selector.xpath("body/div[@id='CommonWealth']//div[@class='row content-main-wrapper']/div[@id='Milk']//div[@class='body-content']/div[@id='FineDining']/p//text()").extract())
        imgHtml = selector.xpath("body/div[@id='CommonWealth']//div[@class='row content-main-wrapper']/div[@id='Milk']//div[@class='body-content']//div[@class='loadme']").extract_first()
        img = None
        if imgHtml:
            img = ''.join(re.findall(".*<source data-srcset=\"(.*?)\?itok",imgHtml,re.S))
        # print(Fr)
        # print(url)
        # print(title)
        # print(pubtime)
        # print(author)
        # print(articalsAncestor)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['ArticalAncestor'] = articalsAncestor
        item['Url'] = url
        item['Title'] = title
        item['Author'] = author
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    '''人民网'''
    def parse_RMW(self, response):
        Fr = "人民网"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@class='clearfix w1000_320 text_title']/h1/text()|body/div[@class='pic_content clearfix']//h1/text()|body/div[@class='text width978 clearfix']/h1/text()").extract()).strip()
        author = ''.join(selector.xpath("body/div[@class='clearfix w1000_320 text_title']/p[@class='author']/text()|body/div[@id='picG']/div[@class='edit clearfix']/i[@id='p_editor']/text()|body/div[@class='text width978 clearfix']/div[@class='edit clearfix']/i[@id='p_editor']/text()").extract()).strip()
        pubtime_A = ''.join(selector.xpath("body/div[@class='clearfix w1000_320 text_title']/div[@class='box01']/div[@class='fl']/text()|body/div[@id='picG']/div[@class='page_c']/text()|body/div[@class='text width978 clearfix']/h2/text()").extract()).strip()
        pubtime_B = re.findall(".*?(\d+)年(\d+)月(\d+)日.*?",pubtime_A,re.S)
        pubtime = ""
        if pubtime_B: pubtime = '-'.join(pubtime_B[0])
        articalsAncestor = ''.join(selector.xpath("body/div[@class='clearfix w1000_320 text_title']/div[@class='box01']/div[@class='fl']/a/text()|body/div[@id='picG']/div[@class='page_c']/a/text()|body/div[@class='text width978 clearfix']/h2/a/text()").extract()).strip()
        content = ''.join(selector.xpath("body/div[@class='clearfix w1000_320 text_con']/div[@class='fl text_con_left']//p/text()|body/div[@id='picG']/p/text()|body/div[@class='text width978 clearfix']/p/text()").extract()).strip()
        imgRel = selector.xpath("body/div[@class='clearfix w1000_320 text_con']/div[@class='fl text_con_left']/div[@class='box_con']//img/@src|body/div[@id='picG']/p//img/@src|body/div[@class='text width978 clearfix']//dd[@id='picG']//img/@src").extract()
        imgsUrlPre_xpath = "http://\w+.people.com.cn"
        urlPre = re.match(imgsUrlPre_xpath, url).group(0)
        if imgRel:
            imgAbs = ""
            for u in imgRel:
                    ck = re.match("http://\S+", u)
                    if ck:
                        imgAbs = imgAbs + u + '\n'
                    else:
                        imgAbs = imgAbs + ''.join([urlPre, u]) + '\n'
        else:
            imgAbs = None
        # print('url', url)
        # print('title',title)
        # print('author',author)
        # print("pubtime",pubtime)
        # print("articalsAncestor",articalsAncestor)
        # print("content",content)
        # print("img",imgAbs)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['ArticalAncestor'] = articalsAncestor
        item['Url'] = url
        item['Title'] = title
        item['Author'] = author
        item['Pubtime'] = pubtime
        item['Img'] = imgAbs
        item['Content'] = content
        yield item

    '''中华网'''
    def parse_ZHW(self, response):
        Fr = "中华网"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@id='chan_mainBlk']/div[@id='chan_mainBlk_lft']/div[@id='chan_newsBlk']/h1[@id='chan_newsTitle']/text()").extract()).strip()
        pubtime_A = ''.join(selector.xpath("body/div[@id='chan_mainBlk']/div[@id='chan_mainBlk_lft']/div[@id='chan_newsBlk']/div[@id='chan_newsInfo']/text()").extract()).strip()
        pubtime = ''.join(re.findall(".*?(\d{4}-\d{2}-\d{2}).*?", pubtime_A, re.S))
        articalsAncestor = ''.join(selector.xpath("body/div[@id='chan_mainBlk']/div[@id='chan_mainBlk_lft']/div[@id='chan_newsBlk']/div[@id='chan_newsInfo']/a/text()").extract()).strip()
        content = ''.join(selector.xpath("body/div[@id='chan_mainBlk']/div[@id='chan_mainBlk_lft']/div[@id='chan_newsBlk']/div[@id='chan_newsDetail']/p/text()[normalize-space()]").extract()).strip()
        img = '\n'.join(selector.xpath("body/div[@id='chan_mainBlk']/div[@id='chan_mainBlk_lft']/div[@id='chan_newsBlk']/div[@id='chan_newsDetail']//img/@src").extract()).strip()
        # print(url)
        # print(title)
        # print(pubtime)
        # print(articalsAncestor)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['ArticalAncestor'] = articalsAncestor
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    '''东方头条'''
    def parse_DFTT(self, response):
        Fr = "东方头条"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@class='section']//div[@class='main_content']/div[@class='article']//div[@class='detail_left_cnt']/div[@class='J-title_detail title_detail']/h1//text()").extract()).strip()
        pubtime = ''.join(selector.xpath("body/div[@class='section']//div[@class='main_content']/div[@class='article']//div[@class='detail_left_cnt']/div[@class='J-title_detail title_detail']/div[@class='share_cnt_p clearfix']/div[@class='fl']/i[1]/text()").extract())[0:10].strip()
        articalsAncestor = ''.join(selector.xpath("body/div[@class='section']//div[@class='main_content']/div[@class='article']//div[@class='detail_left_cnt']/div[@class='J-title_detail title_detail']/div[@class='share_cnt_p clearfix']/div[@class='fl']/i[last()]/text()").extract()).strip()
        content = ''.join(selector.xpath("body/div[@class='section']//div[@class='main_content']/div[@class='article']//div[@class='detail_left_cnt']/div[@id='J-contain_detail_cnt']//p//text()[normalize-space()]").extract()).strip()
        img = ''.join(selector.xpath("body/div[@class='section']//div[@class='main_content']/div[@class='article']//div[@class='detail_left_cnt']/div[@id='J-contain_detail_cnt']//img/@src").extract()).strip()

        # print(title)
        # print(pubtime)
        # print(articalsAncestor)
        # print(content)
        # print(img)
        # print(url)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['ArticalAncestor'] = articalsAncestor
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item
        pass

    '''澎湃新闻'''
    def parse_PPXW(self, response):
        Fr = "澎湃新闻"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@class='bdwd main clearfix']/div[@class='main_lt']/div[@class='newscontent']/h1[@class='news_title']/text()").extract()).strip()
        pubtime = ''.join(selector.xpath("body/div[@class='bdwd main clearfix']/div[@class='main_lt']/div[@class='newscontent']/div[@class='news_about']/p[last()]/text()").extract()).strip()[0:10]
        articalsAncestor = ''.join(selector.xpath("body/div[@class='bdwd main clearfix']/div[@class='main_lt']/div[@class='newscontent']/div[@class='news_about']/p[1]/text()").extract()).strip()
        if "/" in articalsAncestor:
            # print("出现下滑线")
            # print(articalsAncestor)
            articalsAncestor = re.findall(".*?/(.*)",articalsAncestor,re.S)[0]
        content = ''.join(selector.xpath("body/div[@class='bdwd main clearfix']/div[@class='main_lt']/div[@class='newscontent']/div[@class='news_txt']//text()[normalize-space()]").extract()).strip()
        img = '\n'.join(selector.xpath("body/div[@class='bdwd main clearfix']/div[@class='main_lt']/div[@class='newscontent']/div[@class='news_txt']//img/@src|body/div[@class='bdwd main clearfix']/div[@class='main_lt']/div[@class='newscontent']/div[@class='atlas_360']//img/@src").extract()).strip()
        # print(url)
        # print(title)
        # print(pubtime)
        # print(articalsAncestor)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['ArticalAncestor'] = articalsAncestor
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    '''参考消息'''
    def parse_CKXX(self, response):
        Fr = "参考消息"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body//div[@class='bg-content']/h1/text()").extract()).strip().strip()
        pubtime = ''.join(selector.xpath("body//div[@class='bg-content']/span[@id='pubtime_baidu']/text()").extract()).strip()[0:10].strip()
        articalsAncestor = ''.join(selector.xpath("body//div[@class='bg-content']/span[@id='source_baidu']/a/text()").extract()).strip().strip()
        content = ''.join(selector.xpath("body//div[@class='bg-content']/div[@class='inner']/div[@id='ctrlfscont']/p/text()").extract()).strip()
        img= '\n'.join(selector.xpath("body//div[@class='bg-content']/div[@class='inner']/div[@id='ctrlfscont']/p//img/@src").extract()).strip()
        # print(url)
        # print(title)
        # print(pubtime)
        # print(articalsAncestor)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['ArticalAncestor'] = articalsAncestor
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    '''网易新闻'''
    def parse_WY(self, response):
        Fr = "网易新闻"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@class='post_content post_area clearfix']/div[@id='epContentLeft']/h1/text()|body/div[@class='blog-area']/div[@class='main-a clearfix']/div[@class='left']/h1/text()").extract()).strip()
        pubtime = ''.join(selector.xpath("body/div[@class='post_content post_area clearfix']/div[@id='epContentLeft']/div[@class='post_time_source']/text()|body/div[@class='blog-area']/div[@class='main-a clearfix']/div[@class='left']/div[@class='main-info']/p[@id='ptime']/text()").extract()).strip()[0:10]
        articalsAncestor = ''.join(selector.xpath("body/div[@class='post_content post_area clearfix']/div[@id='epContentLeft']/div[@class='post_time_source']/a/text()|body/div[@class='blog-area']/div[@class='main-a clearfix']/div[@class='left']/div[@class='main-info']/p[@id='psource']/a/text()").extract()).strip()
        content = ''.join(selector.xpath("body/div[@class='post_content post_area clearfix']/div[@id='epContentLeft']/div[@class='post_body']/div[@class='post_text']//p/text()|body/div[@class='post_content post_area clearfix']/div[@id='epContentLeft']/div[@class='post_body']/div[@class='end-text']/p/text()|body/div[@class='blog-area']/div[@class='main-a clearfix']/div[@class='left']/div[@id='main-content']//p/text()[normalize-space()]").extract()).strip()
        img= '\n'.join(selector.xpath("body/div[@class='post_content post_area clearfix']/div[@id='epContentLeft']/div[@class='post_body']/div[@class='post_text']//img/@src|body/div[@class='post_content post_area clearfix']/div[@id='epContentLeft']/div[@class='post_body']/div[@class='nph_gallery']/div[@class='nph_bg']//div[@class='nph_cnt']/img/@src|body/div[@class='blog-area']/div[@class='main-a clearfix']/div[@class='left']/div[@id='main-content']//img/@src").extract())
        # print(url)
        # print(title)
        # print(pubtime)
        # print(articalsAncestor)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['ArticalAncestor'] = articalsAncestor
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    '''搜狐'''
    def parse_SHXW(self, response):
        Fr = "搜狐新闻"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@class='wrapper-box']/div[@id='article-container']/div[@class='left main']/div[@class='text']/div[@class='text-title']/h1/text()|body/div[@id='container']//div[@class='content-box clear']/h1/text()").extract()).strip()
        pubtime_A = ''.join(selector.xpath("body/div[@class='wrapper-box']/div[@id='article-container']/div[@class='left main']/div[@class='text']/div[@class='text-title']/div[@class='article-info']/span/@data-val|body/div[@id='container']//div[@class='content-box clear']/div[@class='time-fun clear']/div[@class='time-source']/div[@id='pubtime_baidu']/text()").extract())[0:10]
        if re.match("\d{4}-\d{2}-\d{2}",pubtime_A):
            pubtime = pubtime_A
        else:
            timeArray = time.localtime(int(pubtime_A))
            pubtime = time.strftime("%Y-%m-%d", timeArray)
        content = ''.join(selector.xpath("body/div[@class='wrapper-box']/div[@id='article-container']/div[@class='left main']/div[@class='text']/article[@class='article']/p/text()[normalize-space()]|body/div[@id='container']//div[@class='content-box clear']/div[@id='contentText']//p/text()").extract()).strip()
        img= '\n'.join(selector.xpath("body/div[@class='wrapper-box']/div[@id='article-container']/div[@class='left main']/div[@class='text']/article[@class='article']//p/img/@src|body/div[@id='container']//div[@class='content-box clear']/div[@id='contentText']//img/@src").extract())
        # print(url)
        # print(title)
        # print(pubtime)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    '''搜狐汽车'''
    def parse_SHQC(self,response):
        Fr = "搜狐汽车"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@id='container']/div[@class='content-wrapper']/div[@class='news-info clear']//h1/text()|body/div[@id='contentA']/div[@class='left']/h1/text()").extract()).strip()
        pubtime_A = ''.join(selector.xpath("body/div[@id='container']/div[@class='content-wrapper']/div[@class='news-info clear']//span[@id='pubtime_baidu']/text()|body/div[@id='contentA']/div[@class='left']/div[@class='timeFun clear']//div[@class='time']/text()").extract()).strip()[0:11]
        pubtime_B = re.findall("(\d{4})年(\d{2})月(\d{2})日",pubtime_A)
        pubtime = ""
        if pubtime_B: pubtime = '-'.join(pubtime_B[0])
        content = ''.join(selector.xpath("body/div[@id='container']/div[@class='content-wrapper']/div[@id='contentText']/p//text()|body/div[@id='contentA']/div[@class='left']/div[@id='contentText']//p/text()").extract()).strip()
        img= '\n'.join(selector.xpath("body/div[@id='container']/div[@class='content-wrapper']/div[@id='contentText']/p//img/@src|body/div[@id='contentA']/div[@class='left']/div[@id='contentText']//img/@src").extract())
        # print(url)
        # print(title)
        # print(pubtime)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    '''大众网'''
    def parse_DZW(self, response):
        Fr = "大众网"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@id='xl-headline']/div/h2//text()|body/div[@id='headline']/h1/text()|body/div[@id='wrapper']/h1/text()|body/div[@class='photoMHD']/div[@class='title']//h2/text()|body/div[@id='content']/div[@id='main']/h2/text()").extract()).strip()
        pubtime_ArticalAncestor_Author = ''.join(selector.xpath("body/div[@id='xl-headline']//div[@class='left']/text()|body/div[@id='headline']/i/text()|body/div[@id='wrapper']/div[@id='infor']/div[@class='left']//text()|body/div[@class='photoMHD']/div[@class='title']//p/span[1]/text()|body/div[@id='content']/div[@id='main']/div[@id='infor']/p[2]/text()").extract()).strip()
        # print(pubtime_ArticalAncestor_Author)
        pubtime = pubtime_ArticalAncestor_Author[0:10]
        if '年' in pubtime:
            pubtime = "-".join(re.findall("(\d{4})年(\d{2})月(\d{2})", pubtime)[0])
        articalAncestor = "".join(re.findall(".*来源.(.*?)作者.*",pubtime_ArticalAncestor_Author))
        author = "".join(re.findall(".*作者.(.*)",pubtime_ArticalAncestor_Author))
        content = ''.join(selector.xpath("body/div[@class='layout']/div/div/div[@class='news-con']//p//text()|body/div[@id='main']//div[@class='TRS_Editor']//p/text()|body/div[@id='wrapper']/div[@id='main']//div[@class='TRS_Editor']//p//text()[normalize-space()]|body/div[@class='photoMHD']/div[@class='photoNews']/div[@class='TRS_Editor']/p//text()|body/div[@id='content']/div[@id='main']/div[@id='text']/p/text()|body/div[@class='photoMHD']/div[@class='photoNews']//p[@id='photoDesc']/text()").extract()).strip()
        imgRel = selector.xpath("body/div[@class='layout']/div/div/div[@class='news-con']//p/img/@src|body/div[@id='main']//div[@class='TRS_Editor']/p/img/@src|body/div[@id='wrapper']/div[@id='main']//div[@class='TRS_Editor']//p/img/@src|body/div[@class='photoMHD']/div[@class='photoNews']/div[@class='TRS_Editor']//img/@src|body/div[@id='content']/div[@id='main']/div[@id='imgBox']/div[@id='picDiv']/div[@class='pic']/img/@src|body/div[@class='photoMHD']/div[@id='imgBox']/div[@id='picDiv']/div[@class='pic']/img/@src").extract()
        imgsUrlPre_xpath = "http://\w+.dzwww.com/\S+/\d\d\d\d\d\d/"
        urlPre = re.match(imgsUrlPre_xpath, url).group(0)
        if imgRel:
            imgAbs = ""
            for u in imgRel:
                    ck = re.match("http://\S+", u)
                    if ck:
                        imgAbs = imgAbs  + u + '\n'
                    else:
                        imgAbs = imgAbs  + ''.join([urlPre, u]) + '\n'
        else:
            imgAbs = None
        # print(url)
        # print(title)
        # print(pubtime)
        # print(author)
        # print(articalAncestor)
        # print(content)
        # print(imgAbs)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['ArticalAncestor'] = articalAncestor
        item['Author'] = author
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = imgAbs
        item['Content'] = content
        yield item

    '''新华网'''
    def parse_XHW(self,response):
        Fr = "新华网"
        url= response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("body/div[@class='header']/div[@class='h-p3 clearfix']/div[@class='h-news']/div[@class='h-title']/text()|body/div[@class='center']/div[@class='conW']/div[@class='title clearfix']//span[@id='title']/text()").extract()).strip()
        pubtime = ''.join(selector.xpath("body/div[@class='header']/div[@class='h-p3 clearfix']/div[@class='h-news']/div[@class='h-info']//em[@id='source']/text()|body/div[@class='center']/div[@class='conW']/div[@class='title clearfix']//span[@id='pubtime']/text()").extract()).strip()[0:10]
        if "年" in pubtime:
            pubtime = "-".join(re.findall("(\d{4})年(\d{2})月(\d{2})",pubtime)[0])
        articalsAncestor  = ''.join(selector.xpath("body/div[@class='header']/div[@class='h-p3 clearfix']/div[@class='h-news']/div[@class='h-info']/span[@class='h-time']/text()|body/div[@class='center']/div[@class='conW']/div[@class='title clearfix']//em[@id='source']/text()").extract()).strip()
        content = ''.join(selector.xpath("body/div[@class='main']/div/div[@class='p-right left']/div[@id='p-detail']//p/text()[normalize-space()]|body/div[@class='center']/div[@class='conW']/div[@class='content']//p/text()[normalize-space()]").extract()).strip()
        imgRel = selector.xpath("body/div[@class='main']/div/div[@class='p-right left']/div[@id='p-detail']//p/img/@src|body/div[@class='center']/div[@class='conW']/div[@class='content']//p/img/@src").extract()
        imgsUrlPre_xpath = "http://news.xinhuanet.com/\w+/\d\d\d\d-\d\d/\d\d/"
        urlPre = re.match(imgsUrlPre_xpath, url).group(0)
        if imgRel:
            imgAbs = ""
            for u in imgRel:
                    ck = re.match("http://\S+", u)
                    if ck:
                        imgAbs = imgAbs + u + '\n'
                    else:
                        imgAbs = imgAbs + ''.join([urlPre, url]) + '\n'
        else:
            imgAbs = None
        # print(title)
        # print(articalsAncestor)
        # print(pubtime)
        # print(content)
        # print(imgAbs)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = imgAbs
        item['Content'] = content
        yield item

    '''中国青年网'''
    #图片都是相对地址
    def parse_ZGQNW(self, response):
        Fr = "中国青年网"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("//body/div[@class='main']//div[@class='l_tit']/text()|//body/div[@class='pic_main_tit']/text()|body//div[@class='page_title']/h1/text()|body/div[@class='main']//div[@class='r2_l']/div[@class='con']/div[@class='yth_con']/h1/text()").extract()).strip()
        pubtime = ''.join(selector.xpath("//body/div[@class='main']//div[@class='main_l']//span[@id='pubtime_baidu']/text()|//body/div[@class='pic_main']/div[@class='ina_silde']/div[@class='ina_pic_bottom']//span[@id='pubtime_baidu']/text()|body//div[@class='page_title']//span[@id='page_right']/text()|body/div[@class='main']//div[@class='r2_l']/div[@class='con']/div[@class='yth_con']/div[@class='source]/span[@class='fb_date']/text()").extract()).strip()[5:15]
        articalsAncestor = ''.join(selector.xpath("//body/div[@class='main']//div[@class='main_l']//span[@id='source_baidu']/a//text()|body/div[@class='pic_main']/div[@class='ina_silde']/div[@class='ina_pic_bottom']//span[@id='source_baidu']//text()|body//div[@class='page_title']//span[@id='source_baidu']/a/text()|body/div[@class='main']//div[@class='r2_l']/div[@class='con']/div[@class='yth_con']/div[@class='source]/span[@class='soure1']/a/text()").extract()).replace('\n','').strip()
        content = ''.join(selector.xpath("//body/div[@class='main']//div[@class='article']//p//text()[normalize-space()]|body/div[@class='pic_main']/div/div[@class='content']/div[@class='TRS_Editor']/p/text()|body//div[@class='TRS_Editor']/p/text()|body//div[@id='container']/p/text()[normalize-space()]").extract()).strip()
        imgRel = selector.xpath("//body/div[@class='main']//div[@class='article']//p/img/@oldsrc|body/div[@class='pic_main']/div/div[@class='content']/div[@class='TRS_Editor']/p/img/@oldsrc|body//div[@class='TRS_Editor']//p/img/@src|body//div[@id='container']//img/@src").extract()
        imgsUrlPre_xpath = "http://\w+\.youth\.cn/\S+/\d+/"
        urlPre = re.match(imgsUrlPre_xpath, url).group(0)
        if imgRel:
            imgAbs = ""
            for u in imgRel:
                ck = re.match("http://\S+", u)
                if ck:
                    imgAbs = imgAbs + u + '\n'
                else:
                    imgAbs = imgAbs + ''.join([urlPre, u]) + '\n'
        else:
            imgAbs = None
        # print('url',url)
        # print('title',title)
        # print("pubtime",pubtime)
        # print("articalsAncestor",articalsAncestor)
        # print("content",content)
        # print("imgAbs",imgAbs)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['ArticalAncestor'] = articalsAncestor
        item['Img'] = imgAbs
        item['Content'] = content
        yield item

    '''腾讯谷雨'''
    def parse_TXGY(self, response):
        Fr = "腾讯谷雨"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = selector.xpath("//body/div[@class='header']//h1/text()").extract_first()
        pubtime = ''.join(selector.xpath("//body/div[@class='header']//div[@class='addtion']/text()[normalize-space()]").extract())[3:]
        # author = selector.xpath("//body/div[@class='authorDiv']//div[@class='moreinfo']/div[1]/text()").extract_first()
        content = selector.xpath("//body/div[@class='header']//div[@class='detail']/p/text()").extract_first()
        img = '\n'.join(selector.xpath("//body/div[@class='container layout']/div[@id='article']/div[@id='articleContent']/div/img/@src").extract())
        # print(url)
        # print("title",title)
        # print("pubtime",pubtime)
        # # print("author",author)
        # print("content",content)
        # print("img",img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    '''腾讯通用'''
    def parse_TX(self, response):
        Fr = "腾讯"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("//body//div[@id='Main-Article-QQ']//div[@class='hd']/h1/text()|//body//div[@class='title']/h1/text()").extract())
        author = ''.join(selector.xpath("//body//div[@id='Main-Article-QQ']//div[@class='hd']/div//span[@class='color-a-3']//text()").extract())
        articalsAncestor = ''.join(selector.xpath("//body//div[@id='Main-Article-QQ']//div[@class='hd']/div//span[@class='a_source']//text()").extract())
        pubtime = ''.join(selector.xpath("//body//div[@id='Main-Article-QQ']//div[@class='hd']//span[@class='a_time']/text()|//body//div[@id='Main-Article-QQ']//div[@class='hd']/div//span[@class='article-time']//text()").extract())[0:10]
        content= ''.join(selector.xpath("//body//div[@id='Main-Article-QQ']//div[@class='bd']//div[@id='Cnt-Main-Article-QQ']//p//text()[name(..)!='script'][name(..)!='style'][normalize-space()]").extract())
        img = '\n'.join(selector.xpath("//body//div[@id='Main-Article-QQ']//div[@class='bd']//div[@id='Cnt-Main-Article-QQ']//img/@src").extract())
        # print(url)
        # print("title:",title)
        # print("author:",author)
        # print("articalsAncestor:",articalsAncestor)
        # print("pubtime:",pubtime)
        # print("content:",content)
        # print("img:",img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['ArticalAncestor'] = articalsAncestor
        item['Author'] = author
        item['Img'] = img
        item['Content'] = content
        yield item

    '''环球网-图集'''
    def parse_HQTJ(self, response):
        #环球网，图片数据都放在script中，以json格式保存
        Fr = "环球图集"
        url= response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("//body/div[@class='container']/div[@class='main']/div[@class='focus_box']/h1/strong/text()").extract())
        pubtime = ''.join(selector.xpath("//body/div[@class='container']/div[@class='main']/div[@class='focus_box']/div[@class='tool']//li[@class='time']//span/text()").extract())[0:10]
        imgs = ''.join(selector.xpath("//body/div[@class='container']/div[@class='main']/div[@class='focus_box']/div[@class='mod']/div[@class='m_r']/script").extract())
        img = ""
        content = ""
        s = imgs.strip('</script>').strip('<script>').strip().strip('var imgData =').strip()
        s = s.strip(';').strip()
        if s:
            js = json.loads(s)
            img = js['img'][0]['img_url']
            content = js['img'][0]['title']
        # print(title)
        # print(pubtime)
        # print(img)
        # print(content)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    '''环球网'''
    def parse_HQW(self, response):
        Fr = "环球网"
        url= response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("//body/div[@class='main']/div[@class='mainCon']/div[@class='con']/div[@class='conLeft']/div[@class='conText']/h1/text()").extract()).strip()
        pubtime = ''.join(selector.xpath("//body/div[@class='main']/div[@class='mainCon']/div[@class='con']/div[@class='conLeft']/div[@class='conText']/div[@class='summaryNew']/strong[@class='timeSummary']/text()").extract()).strip()[0:10]
        articalsAncestor = ''.join(selector.xpath("//body/div[@class='main']/div[@class='mainCon']/div[@class='con']/div[@class='conLeft']/div[@class='conText']/div[@class='summaryNew']/strong[@class='fromSummary']//text()").extract()).strip()
        content = ''.join(selector.xpath("//body/div[@class='main']/div[@class='mainCon']/div[@class='con']/div[@class='conLeft']/div[@class='conText']/div[@class='text']//p/text()").extract()).strip()
        img = '\n'.join(selector.xpath("//body/div[@class='main']/div[@class='mainCon']/div[@class='con']/div[@class='conLeft']/div[@class='conText']/div[@class='text']/p/img/@src").extract()).strip()
        # imgIntro = ''.join(selector.xpath("//body/div[@class='main']/div[@class='mainCon']/div[@class='con']/div[@class='conLeft']/div[@class='conText']/div[@id='text']/p//text()").extract())
        # print(url)
        # print('title',title)
        # print('pubtime',pubtime)
        # print('articalAncestor',articalAncestor)
        # print('content',content)
        # print('img',img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['ArticalAncestor'] = articalsAncestor
        item['Img'] = img
        item['Content'] = content
        yield item

    '''凤凰网'''
    def parse_FHW(self,response):
        Fr = "凤凰网"
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        titles = selector.xpath('//body/div[@class="main"]/div[@class="left"]/div[@id="artical"]/h1[@id="artical_topic"]/text()|//body/div[@class="yc_main wrap"]/div[@class="yc_tit"]/h1/text()').extract()
        pubtime = "".join(selector.xpath('//body/div[@class="main"]/div[@class="left"]/div[@id="artical"]/div[@id="artical_sth"]/p[@class="p_time"]/span[@class="ss01"]/text()|//body/div[@class="yc_main wrap"]/div[@class="yc_tit"]/p/span/text()').extract())[0:10]
        if "年" in pubtime:
            pubtime = "-".join(re.findall("(\d{4})年(\d{2})月(\d{2})",pubtime)[0])
        contents = selector.xpath('//body/div[@class="main"]/div[@class="left"]/div[@id="artical"]/div[@id="artical_real"]/div[@id="main_content"]//p/text()[normalize-space()]|//body/div[@class="yc_main wrap"]/div[@class="yc_con clearfix"]/div[@class="yc_con_l"]/div[@id="yc_con_txt"]/p/text()[normalize-space()]').extract()
        articalAncestors = selector.xpath('//body/div[@class="main"]/div[@class="left"]/div[@id="artical"]/div[@id="artical_sth"]/p[@class="p_time"]//span[@class="ss03"]//text()|//body/div[@class="yc_main wrap"]/div[@class="yc_tit"]/p/a/text()').extract()
        authors = selector.xpath('//body/div[@class="main"]/div[@class="left"]/div[@id="artical"]/div[@id="artical_sth"]/p[@class="p_time"]/span[@itemprop="author"]/span[@itemprop="name"]/text()').extract()
        imgs = selector.xpath('//body/div[@class="main"]/div[@class="left"]/div[@id="artical"]/div[@id="artical_real"]/div[@id="main_content"]//p//img/@src|//body/div[@class="yc_main wrap"]/div[@class="yc_con clearfix"]/div[@class="yc_con_l"]/div[@id="yc_con_txt"]/p[@class="detailPic"]/img/@src').extract()
        # imgsIntros = selector.xpath('//body/div[@class="main"]/div[@class="left"]/div[@id="artical"]/div[@id="artical_real"]/div[@id="main_content"]/p[@class="picIntro"]/span/text()').extract()
        url = response.url
        title = ''.join(titles).strip()
        content = '---'.join(contents).strip()
        articalsAncestor = '---'.join(articalAncestors).strip()
        author = '---'.join(authors).strip()
        img = '\n'.join(imgs).strip()
        # imgsIntro = '---'.join(imgsIntros)
        # print(url)
        # print(title)
        # print(author)
        # print(pubtime)
        # print(articalAncestor)
        # print(content)
        # print(img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Author'] = author
        item['ArticalAncestor'] = articalsAncestor
        item['Img'] = img
        item['Content'] = content
        yield item

    '''新浪'''
    # 博客
    def parse_XLBK(self, response):
        Fr = "新浪博客"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("//body/div[@id='sinabloga']/div[@id='sinablogb']/div[@class='sinablogbody']/div[@id='column_2']/div/div[@class='SG_connBody']/div[@id='articlebody']/div[@class='articalTitle']/h2/text()").extract())
        pubtime = ''.join(selector.xpath("//body/div[@id='sinabloga']/div[@id='sinablogb']/div[@class='sinablogbody']/div[@id='column_2']/div/div[@class='SG_connBody']/div[@id='articlebody']/div[@class='articalTitle']/span[@class='time SG_txtc']/text()").extract())[1:11]
        author = ''.join(selector.xpath("//body/div[@id='sinabloga']/div[@id='sinablogb']/div[@class='sinablogbody']/div[@id='column_1']//strong[@id='ownernick']/text()").extract())
        content = ''.join(selector.xpath(
            "//body/div[@id='sinabloga']/div[@id='sinablogb']/div[@class='sinablogbody']/div[@id='column_2']/div/div[@class='SG_connBody']/div[@id='articlebody']/div[@id='sina_keyword_ad_area2']//text()[normalize-space()]").extract()).strip()
        img = '\n'.join(selector.xpath(
            "//body/div[@id='sinabloga']/div[@id='sinablogb']/div[@class='sinablogbody']/div[@id='column_2']/div/div[@class='SG_connBody']/div[@id='articlebody']/div[@id='sina_keyword_ad_area2']//img/@real_src").extract())
        # print('title', title)
        # print('pubtime', pubtime)
        # print('author',author)
        # print('content', content)
        # print('img', img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['Author'] = author
        item['Img'] = img
        item['Content'] = content
        yield item

    # 军事
    def parse_XLJS(self, response):
        Fr = "新浪军事"
        url= response.url
        #新浪军事
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        # title = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@class='page-header']/h1/text()").extract())
        title = ''.join(selector.xpath("//body/div[@class='main_content']/h1[@id='main_title']/text()").extract())
        pubtime = ''.join(selector.xpath("//body/div[@class='main_content']/div[@id='page-tools']/span/span[@class='titer']/text()").extract()).strip()[0:10]
        if "年" in pubtime:
            pubtime = "-".join(re.findall("(\d{4})年(\d{2})月(\d{2})",pubtime)[0])
        # pubtime = ''.join(re.findall('http://.*?\.sina\.com\.cn/.*?/(\d+-\d+-\d+)/.*?',response.url))
        articalsAncestor = ''.join(selector.xpath("//body/div[@class='main_content']/div[@id='page-tools']/span/span[@class='source']//text()").extract())
        # content = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@id='articleContent']/div[@class='left']/div[@id='artibody']/p//text()").extract())
        content = ''.join(selector.xpath("//body/div[@class='main_content']/div[@id='wrapOuter']/div[@class='content_wrappr_left']/div[@id='artibody']//p//text()").extract())
        img = '\n'.join(selector.xpath("//body/div[@class='main_content']/div[@id='wrapOuter']/div[@class='content_wrappr_left']/div[@id='artibody']//img/@src").extract())
        # print(url)
        # print('title',title)
        # print('pubtime',pubtime)
        # print('articalAncestor',articalAncestor)
        # print('content',content)
        # print('img',img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['ArticalAncestor'] = articalsAncestor
        item['Img'] = img
        item['Content'] = content
        yield item

    #财经
    def parse_XLCJ(self, response):
        Fr = "新浪财经"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@class='page-header']/h1/text()").extract())
        pubtime = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@class='page-info']/span/text()").extract()).strip()[0:10]
        if "年" in pubtime:
            pubtime = "-".join(re.findall("(\d{4})年(\d{2})月(\d{2})",pubtime)[0])
        articalsAncestor = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@class='page-info']/span/span/a/text()").extract())
        content = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@id='articleContent']/div[@class='left']/div[@id='artibody']/p//text()").extract())
        img = '\n'.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@id='articleContent']/div[@class='left']/div[@id='artibody']//img/@src").extract())
        # print(url)
        # print('title',title)
        # print('pubtime',pubtime)
        # print('articalAncestor',articalAncestor)
        # print('content',content)
        # print('img',img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['ArticalAncestor'] = articalsAncestor
        item['Img'] = img
        item['Content'] = content
        yield item

    # 专栏
    def parse_XLZL(self, response):
        Fr = "新浪专栏"
        url = response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        title = ''.join(selector.xpath(
            "//body/div[@class='wrap']/div/div[@class='blkContainer']/div[@id='J_Article_Wrap']/div[@class='blkContainerSblk']/h1[@id='artibodyTitle']/text()").extract())
        pubtime = ''.join(selector.xpath("//body/div[@class='wrap']/div/div[@class='blkContainer']/div[@id='J_Article_Wrap']/div[@class='blkContainerSblk']/div[@class='artInfo']/span[@id='pub_date']/text()").extract())[0:10]
        if "年" in pubtime:
            pubtime = "-".join(re.findall("(\d{4})年(\d{2})月(\d{2})",pubtime)[0])
        author  = ''.join(selector.xpath("//body/div[@class='wrap']/div/div[@class='blkContainer']/div[@id='J_Article_Wrap']/div[@class='blkContainerSblk']/div[@class='artInfo']/span[@id='author_ename']//a/text()").extract())
        content = ''.join(selector.xpath("//body/div[@class='wrap']/div/div[@class='blkContainer']/div[@id='J_Article_Wrap']/div[@class='blkContainerSblk']/div[@id='artibody']/p/text()").extract()).strip()
        img = '\n'.join(selector.xpath("//body/div[@class='wrap']/div/div[@class='blkContainer']/div[@id='J_Article_Wrap']/div[@class='blkContainerSblk']/div[@id='artibody']/div[@class='img_wrapper']/img/@src").extract()).strip()
        # print(url)
        # print('title', title)
        # print('author',author)
        # print('pubtime', pubtime)
        # print('content', content)
        # print('img',img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Author'] = author
        item['Pubtime'] = pubtime
        item['Img'] = img
        item['Content'] = content
        yield item

    # 通用
    def parse_XLTY(self, response):
        Fr = "新浪通用"
        url= response.url
        selector = Selector(response)
        referer = response.request.headers['Referer']
        fromWord = unquote(''.join(re.findall(".*\?word=(.*?)&.*?", str(referer))))
        # title = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@class='page-header']/h1/text()").extract())
        title = ''.join(selector.xpath("//body//h1[@id='artibodyTitle']/text()|body//h1[@id='main_title']/text()").extract())
        pubtime = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@id='page-info']/span/text()|body/div[@class='main_content']/div[@id='page-tools']/span[@class='time-source']/span[@class='titer']/text()").extract()).strip()[0:10]
        if "年" in pubtime:
            pubtime = "-".join(re.findall("(\d{4})年(\d{2})月(\d{2})",pubtime)[0])
        articalsAncestor = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@id='page-info']/span/span/span/a/text()|body/div[@class='main_content']/div[@id='page-tools']/span[@class='time-source']/span[@class='source']/text()").extract())
        # content = ''.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@id='articleContent']/div[@class='left']/div[@id='artibody']/p//text()").extract())
        content = ''.join(selector.xpath("//body//div[@id='artibody']//p//text()[normalize-space()]").extract()).strip()
        img = '\n'.join(selector.xpath("//body/div[@id='wrapOuter']/div[@class='wrap-inner']/div[@id='articleContent']/div[@class='left']/div[@id='artibody']//img/@src|body/div[@class='main_content']//div[@id='artibody']//img/@src").extract())
        # print('title',title)
        # print('pubtime',pubtime)
        # print('articalAncestor',articalAncestor)
        # print('content',content)
        # print('img',img)
        item = TigerItem()
        item['From'] = Fr
        item['FromWord'] = fromWord
        item['Url'] = url
        item['Title'] = title
        item['Pubtime'] = pubtime
        item['ArticalAncestor'] = articalsAncestor
        item['Img'] = img
        item['Content'] = content
        yield item

    # 大鱼的池塘
    # def parse(self, response):
    #     # URLgroup = LinkExtractor(allow=("http://brucedone.com/archives/(\d+)"),deny=("http://brucedone.com/archives/(\d+)\?replytocom=(\d+)")).extract_links(response)
    #     # for link in URLgroup:
    #     #     # print(link.url)
    #     # print(response.url)
    #     # print("hello,i am in parse!")

    # def process_results(self, response, results):
    # # print(response.url)
    # selector = Selector(response)
    # titles = selector.xpath('//body/div[@class="main"]/div[@class="left"]/div[@id="artical"]/h1[@id="artical_topic"]/text()').extract()
    # title = ''.join(titles)
    # # print(title,'here is result')
    # return

