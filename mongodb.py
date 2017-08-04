import pymongo

connection = pymongo.MongoClient()
tdb = connection.BD
post_info = tdb.HotWord


# 插入
# one = {"HotWord": "修今生", "HotWordType": "500", "BDHotWordLink": "http://news.baidu.com/ns?word=%E4%BF%AE%E4%BB%8A%E7%94%9F&tn=news&ct=1&from=news&cl=2&rn=20"}
# two = {"HotWord": "刚刚好", "HotWordType": "500", "BDHotWordLink": "http://news.baidu.com/ns?word=%E5%88%9A%E5%88%9A%E5%A5%BD&tn=news&ct=1&from=news&cl=2&rn=20"}
# three = {"HotWord": "演员", "HotWordType": "500", "BDHotWordLink": "http://news.baidu.com/ns?word=%E6%BC%94%E5%91%98&tn=news&ct=1&from=news&cl=2&rn=20"}
# post_info.insert(one)
# post_info.insert(two)
# post_info.insert(three)
# print("插入完成")

# 输出
c = tdb.HotWord.find()
for i in range(0,10):
    print(c[i])

connection.close()