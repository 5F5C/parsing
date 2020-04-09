import requests
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from zillow.zillow import settings
from zillow.zillow.spiders.zillow import ZillowSpider


if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings=craw_settings)

    crawler_proc.crawl(ZillowSpider)
    crawler_proc.start()