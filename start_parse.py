from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from habr_top_weekly import settings
from habr_top_weekly.spiders.habr_top_week import HabrTopWeekSpider

if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings=craw_settings)
    crawler_proc.crawl(HabrTopWeekSpider)
    crawler_proc.start()