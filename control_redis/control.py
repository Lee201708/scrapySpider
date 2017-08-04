
from  redis import Redis
from scrapy.utils.project import get_project_settings
import json
import os

class Connection(object):


    def __init__(self):
        seetings = get_project_settings()
        self.HOST = seetings.get('REDIS_HOST')
        self.PORT = seetings.get('REDIS_PORT')

if __name__ == "__main__":

    connection = Connection()
    # print('HOST:'+str(connection.HOST),'PORT:'+str(connection.PORT))
    r = Redis(host=connection.HOST, port=connection.PORT)
    key = input('输入redis键：')
    val =input('请输入网址：')
    # print(start_url)
    if r.lpush(key,val):
        print('键值存入成功！')
    else:
        print('存入失败！')









