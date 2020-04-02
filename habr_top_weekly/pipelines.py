# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
# class HabrTopWeeklyPipeline(object):
#     def __init__(self):
#         client_mn = MongoClient('mongodb://db_server:27017')
#         self.db_mn = client_mn['habr_scrapy']
    #
    # def format(self, lst: list):
    #     new_list = []
    #     for itm in lst:
    #         new_list.append(itm.replace("\n", ''))
    #     # str = str.replace("\xa0", ' ')
    #     return new_list
#
#     def process_item(self, item, spider):
#         print(item)
#         collection = self.db_mn[spider.name]
#         item['habs'] = self.format(item['habs'])
#         item['title'] = item['title'].replace(u"\xa0", u' ')
#         print(item)
#         collection.insert_one(item)

class InstagramPipline(object):
    def __init__(self):
        client_mn = MongoClient('mongodb://db_server:27017')
        self.db_mn = client_mn['instagram']

    def process_item(self, item, spider):
        collection_name = ''
        if item.keys().__contains__('follower'):
            collection_name = f'{item["user_name"]}_followers'
        else: collection_name = f'{item["user_name"]}_following'
        print(item)
        collection = self.db_mn[spider.name]
        collection[collection_name].insert_one(item)

