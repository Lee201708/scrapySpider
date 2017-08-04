'''
 * 功能： 爬虫数据定义
 * 作者：
 * 创建： 2017-3-3
 * 更新：
 * 修改：
'''
# -*- coding: utf-8 -*-
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field

######NetWorm hotword layer #########################################################################
class BaiduHotWordItem(Item):
    # typeNameLink = Field()
    # typeName = Field()
    HotWord = Field()
    HotWordType = Field()               #词源---热词类型            例如：汽车，美食
    BDHotWordLink = Field()
    WXHotWordLink = Field()
    WBHotWordLink = Field()



######NetWorm Search layer ##############################################################################
class BaiduNewItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    FromWordType = Field()              #热词类型            例如：汽车，美食
    FromWord = Field()                  #来自哪个热词        例如：乐天，特斯拉
    Title = Field()
    TitleLink = Field()
    pass



######NetWorm Tiger layer ##############################################################################
class TigerItem(Item):
    Url = Field()
    Title = Field()
    Author = Field()
    Pubtime = Field()
    Source = Field()                    #新闻来源                                  例如：百度，搜狗，谷歌
    From = Field()                      #新闻来源（在哪个网站找到的）               例如：凤凰，网易
    ArticalAncestor = Field()           #最初创始网站
    FromWord = Field()                  #词源
    WordType = Field()                  #类型
    Audio = Field()
    Voice = Field()
    Img = Field()
    ImgIntro = Field()                  #图片介绍
    Content = Field()

class PhotoItem(Item):
    Url = Field()
    Title = Field()
    Src = Field()
    Intro = Field()
