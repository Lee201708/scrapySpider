'''
作者：Lee
日期：2017/04/27
功能：爬虫3 MediaSpider:dupefilter 恢复

'''
from  redis import Redis
from scrapy.utils.project import get_project_settings
import json
import os
import hashlib

class Connection(object):


    def __init__(self):
        seetings = get_project_settings()
        self.HOST = seetings.get('REDIS_HOST')
        self.PORT = seetings.get('REDIS_PORT')

    def fileOpen(self,name):
        try:
            file = open(name,'r',encoding='utf-8')
            return file
        except IOError as err:
            print("File Error:" + str(err))  # str()将对象转换为字符串

    def scan_files(self,directory, prefix=None, postfix=None):
        files_list = []
        for root, sub_dirs, files in os.walk(directory):
            for special_file in files:
                if postfix:
                    if special_file.endswith(postfix):
                        files_list.append(os.path.join(root, special_file))
                elif prefix:
                    if special_file.startswith(prefix):
                        files_list.append(os.path.join(root, special_file))
                else:
                    files_list.append(os.path.join(root, special_file))
        return files_list


if __name__ == "__main__":

    connection = Connection()
    r = Redis(host=connection.HOST, port=connection.PORT)
    list = connection.scan_files(directory='../json/', prefix='NewsSpider', postfix=None)
    for file_name in list:
        print(file_name, '-------------------------------------------------------------------------')
        file = connection.fileOpen(file_name)
        for i in file:
            line = json.loads(i)
            TitleLink = line['TitleLink']
            TitleLinks = hashlib.sha1(TitleLink.encode('utf-8')).hexdigest()
            if r.sadd('MediaSpider:dupefilter', TitleLinks):
                print('插入成功', TitleLink)
            else:
                print('插入失败-------------', TitleLink)
