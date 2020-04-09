# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from zillow.zillow.items import ZillowItem
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['http://www.zillow.com/san-francisco-ca/']
    browser = webdriver.Firefox()

    def parse(self, response):
        for pag_url in response.xpath('//nav[@aria-label="Pagination"]/ul/li/@href'):
            if not pag_url:
                yield response.follow(pag_url, callback=self.parse, dont_filter=True)
            yield response.follow(pag_url, callback=self.parse)

        for ads_url in response.xpath(
            '//ul[contains(@class, "photo-cards_short")]/li/article/div[@class="list-card-info"]/a/@href'):
            yield response.follow(ads_url, callback=self.ads_parse)

    def ads_parse(self, response):
        item = ItemLoader(ZillowItem(), response)
        self.browser.get(response.url)
        media_col = self.browser.find_element_by_css_selector('.ds-media-col')
        photo_pic_len = len(
            self.browser.find_element_by_xpath('//ul[@class="media-stream"]/li/picture/source[@type="image/jpeg"]')
        )
        while True:
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            tmp = len(
                self.browser.find_element_by_xpath('//ul[@class="media-stream"]/li/picture/source[@type="image/jpeg"]')
            )
            if tmp == photo_pic_len:
                break
            photo_pic_len = tmp

        images = [
            itm for itm in
            self.browser.find_element_by_xpath('//ul[@class="media-stream"]/li/picture/source[@type="image/jpeg"]')
        ]
        item.add_value('photos', images)
        item.add_value('url', response.url)
        print(1)
        yield item.load_item()