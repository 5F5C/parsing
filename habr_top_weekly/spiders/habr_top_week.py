# -*- coding: utf-8 -*-
import datetime
import scrapy


class HabrTopWeekSpider(scrapy.Spider):
    name = 'habr_top_week'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/top/weekly']

    def parse(self, response):
        pagination_urls = response.css('ul.toggle-menu.toggle-menu_pagination li a::attr("href")').extract()
        for itm in pagination_urls:
            yield response.follow(itm, callback=self.parse)

        for post_url in response.css('a.post__title_link::attr("href")'):
            yield response.follow(post_url, callback=self.post_parse)

    def post_parse(self, response):
        data = {
            'title': response.css('span.post__title-text::text').extract_first(),
            'autor': response.css('span.user-info__nickname.user-info__nickname_small::text').extract_first(),
            'autor_url': response.css('a.post__user-info.user-info::attr("href")').extract_first(),
            'date': response.css('span.post__time::attr("data-time_published")').extract_first(),
            'tags': response.css('ul.inline-list.inline-list_fav-tags.js-post-tags a::text').extract(),
            'habs': response.css('ul.inline-list.inline-list_fav-tags.js-post-hubs a::text').extract(),
            'comments_count': response.css('span.post-stats__comments-count::text').extract_first(),
            'parse_date': str(datetime.datetime.now().date())
        }
        yield data