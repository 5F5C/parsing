# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class ZillowPipeline(object):

    def __init__(self):
        client_mn = MongoClient('mongodb://db_server:27017')
        self.db_mn = client_mn['zillow']

    def process_item(self, item, spider):
        collection = self.db_mn[spider.name]
        item['habs'] = self.format(item['habs'])
        item['title'] = item['title'].replace(u"\xa0", u' ')
        print(item)
        collection.insert_one(item)
        return item

class ImgPipeLine(ImagesPipeline):

    def get_media_requests(self, item, info):

        if item.get('photos'):
            for img_url in item['photos']:
                try:
                    yield scrapy.Request(img_url)
                except Exception as e:
                    pass
    def item_completed(self, results, item, info):

        if results:
            item['photos'] = [itm[1] for itm in results]
        return item