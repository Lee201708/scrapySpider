# -*- coding: utf-8 -*-
'''这个是用来存储全局变量的公共模块'''


'''使用的时候，首先引入本文件，然后在主模块中 public_variable._init()

    在 a.py
    public_variable.set_value('Key1','Value')
    public_variable.set_value('Key2','Value')

    在 b.py
    M = public_variable.get_value('Key')
    N = public_variable.get_value('Key')
'''
'''
    这样就可以在不同模块中，共用某个变量，实现特定的判定。
    类似在 pipeline 中需要根据 dupeCount 的值，决定是否停止 执行异常---CloseSpider()
'''




def _init():#初始化
    global _global_dict
    _global_dict = {}

""" 定义一个全局变量 """
def set_value(key,value):
    global _global_dict
    _global_dict[key] = value


""" 获得一个全局变量,不存在则返回默认值 """
def get_value(key,defValue=None):
    global _global_dict
    try:
        return _global_dict[key]
    except KeyError:
        return defValue


# def _init():
#     global IncreaseTime
#     IncreaseTime = None
#
# def set_value(value):
#     global IncreaseTime
#     IncreaseTime = value
#
# def get_value(defauValue=None):
#     try:
#         return IncreaseTime
#     except:
#         return defauValue