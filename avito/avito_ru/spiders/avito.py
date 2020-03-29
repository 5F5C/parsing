# -*- coding: utf-8 -*-
# Задание:
#
# Источник: https://www.avito.ru/ раздел недвижимость квартиры
#
# Извлекаем слуд параметры:
# - заголовок
# - url объявления
# - дата публикации
# - все фото
# - имя и ссылка на автора объявления
# - список параметров объявления из этого блока (https://www.dropbox.com/s/e1dho7iwom93fnb/%D0%A1%D0%BA%D1%80%D0%B8%D0%BD%D1%88%D0%BE%D1%82%202020-03-26%2022.11.42.png?dl=0)
# - телефон если получится
#
# обязательно использовать Item и ItemLoader


import scrapy
from scrapy.loader import ItemLoader
from avito_ru.items import AvitoRuItem

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/moskva_i_mo/kvartiry']

    def parse(self, response):
        for num in response.xpath('//div[@data-marker="pagination-button"]//span/text()').extract():
            try:
                num = int(num)
                yield response.follow(f'{self.start_urls[0][20:]}?p={num}', callback=self.parse)
            except TypeError as e:
                continue
            except ValueError as e:
                continue

        for ads_url in response.css('div.item_table-wrapper h3.snippet-title a.snippet-link::attr("href")').extract():
            yield response.follow(ads_url, callback=self.ads_parse)

    def ads_parse(self, response):
        item = ItemLoader(AvitoRuItem(), response)
        item.add_css('title', 'h1.title-info-title span::text')
        item.add_value('url', response.url)
        item.add_xpath('photos', '//div[contains(@class, "gallery-img-frame")]/@data-url')
        item.add_css('date', 'div.title-info-metadata-item-redesign::text')
        item.add_xpath('autor', '//div[contains(@class, "seller-info-name js-seller-info-name")]/a/text()')
        autor_url = response.css('div.seller-info-name.js-seller-info-name a::attr("href")')
        autor_url = f'{self.start_urls[:20]}{autor_url}'
        item.add_value('autor_url', autor_url)
        params = response.css('ul.item-params-list li span::text').extract()
        values = response.css('ul.item-params-list li::text').extract()
        values[::2] = params
        params = {values[i]: values[i + 1] for i in range(0, len(values), 2)}
        item.add_value('param', params)

        yield item.load_item()
