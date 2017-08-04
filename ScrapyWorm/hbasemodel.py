import happybase
import time
#传递一个字典，指定行插入数据
#字典格式如：
# dd={'cf:title':'dd','cf:time':'time'}
# cc={'cf:title':'dd'}
#
#用法：import hbasemodel.py
#调用：getDict()
#传入：一个字典

class HBASE(object):
    def __init__(self):
        #本地测试
        # self.host = '192.168.3.158'
        # self.port = 9090
        # self.host = '10.0.5.10'
        #生产测试
        # self.host = '54.223.187.46'
        self.host = '192.168.1.57'
        self.port = 9090
        self.table_name = 'news'
        try:
            connection = happybase.Connection(self.host,port=self.port)
            self.tabl = connection.table(self.table_name)
        except ConnectionError as err:
            print("链接错误%s，即将重新链接"%err)
    def connect_hbase(self):
        try:
            connection = happybase.Connection(self.host,port=self.port)
            self.tabl = connection.table(self.table_name)
        except ConnectionError as err:
            print("链接错误%s，即将重新链接"%err)


    def saveDict(self,dictInfo):
        t = int(time.time() * 1000)
        try:
            self.tabl.put(('row_%13d' % t).encode('ascii'), dictInfo)
            print('存储成功')
        except Exception as err:
            print("插入到Hbase失败，错误详情%s"%err)
            self.connect_hbase()



if __name__ == '__main__':
    pass

# getDict(dd)


    # if table.row(('row_%13d'%t).encode('ascii'))=:
    #     pass
    # print(('row_%13d'%t).encode('ascii'))
    # print(table.row(('row_%13d'%t).encode('ascii')))
# def getDict(adddict):
#     table.put('row13',adddict)
#     print(table.row('row13'))
# getDict(cc)
# getDict({'cf:title':'dd','cf：time':'time}'})
# def getDict(adddict):
#     with table.batch() as b:
#         # print('ddd')
#         b.put('row13',adddict)
#         # for i in range(5):
#         #     b.put(('row_title_%03d'%i).encode('ascii'),adddict)
#         #     print(table.row(('row_title_%03d'%i).encode('ascii')))
#     #table.put('row1',adddict)
# getDict({'cf:title':'dd','cf：time':'time}'})
# def getDict(dd):
#     t=time.time()*1000
#     int(t)
#     table.put(('row_%13d'%t).encode('ascii'),dd)
#     print(('row_%13d'%t).encode('ascii'))
#     print(table.row(('row_%13d'%t).encode('ascii')))
# getDict(dd)
# with table.batch(batch_size=10) as b:
#     for i in range(5):
#         b.put(('row_title_%07d'%i).encode('ascii'),dd)
#     # b.put('row14',dd)
#         print(('row_title_%07d'%i).encode('ascii'))
#         print(table.row(('row_title_%03d'%i).encode('ascii')))
