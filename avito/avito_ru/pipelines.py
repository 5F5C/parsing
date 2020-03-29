# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from pymongo import MongoClient
import re

class AvitoRuPipeline(object):
    def __init__(self):
        client = MongoClient('mongodb://db_server:27017/')
        self.db = client['avito']

    def process_item(self, item, spider):
        item['autor'] = item['autor'].replace("\n", '')
        item['date'] = item['date'].replace("\n", '')
        item['autor_url'] = item['autor_url'].replace("\n", '')
        print(item)
        collection = self.db[spider.name]
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