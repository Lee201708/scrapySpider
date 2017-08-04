
from scrapy import log
from  ScrapyWorm.items import BaiduHotWordItem



class SaveHotWordPipeline(object):
    def process_items(self,item,spider):
        if isinstance(item,BaiduHotWordItem):
            # check = FirDBSaveHotWord(item['hotWord'])
            # if check:
            #     log.msg('插入FirDB成功')
            # else:
            #     log.msg('插入FirDB失败',level=log.WARNING)
            pass
        return item
