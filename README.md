# scrapySpider
scrapy爬虫
scrapy爬虫主要由两部分组成，第一部分百度热词爬虫，第二部分新闻内容爬虫
#  百度热词爬虫
起始链接：http://top.baidu.com/add?fr=topbuzz_b1   <br/>
抓取热词榜内容，并通过拼接字符串，生成对应的百度搜索链接  <br/>
例：  <br/>
热词---战狼2   <br/>
对应百度搜索链接---http://news.baidu.com/ns?word=%E6%88%98%E7%8B%BC2&tn=news&ct=1&from=news&cl=2&rn=20    <br/>
将热词和热词对应搜索链接存入redis，供第二部分新闻内容爬虫使用，在存入redis前，首先通过   <br/>
if r.sadd('HotWord:dupefilter',hotword):    <br/>
判断当前热词是否已存在，若不存在，则  <br/>
r.lpush('BDMedia:urls',item['BDHotWordLink'])   <br/>
否则   <br/>
raise DropItem("Duplicate item found: %s" % item)    <br/>

#  新闻内容爬虫
读取BDMedia:urls中的内容，获取新闻搜索页面，并通过LinkExtractor，自动匹配页面中所有符合匹配规则的链接，调用对应的回调函数，对链接新闻内容进行抓取。
