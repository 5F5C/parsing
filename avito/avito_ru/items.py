# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst

def clean_photo(values):
    if values[:2] == '//':
        return f'http:{values}'
    return values

class AvitoRuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    date = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(clean_photo))
    autor = scrapy.Field(output_processor=TakeFirst())
    autor_url = scrapy.Field(output_processor=TakeFirst())
    param = scrapy.Field(output_processor=TakeFirst())
    pass
