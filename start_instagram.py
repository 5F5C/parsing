import os
from dotenv import  load_dotenv
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from habr_top_weekly import settings
from habr_top_weekly.spiders.instagram import InstagramSpider


env_path = Path(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

if __name__ == '__main__':
    craw_settings = Settings()
    craw_settings.setmodule(settings)
    crawler_proc = CrawlerProcess(settings=craw_settings)

    crawler_proc.crawl(InstagramSpider, logpass=(os.getenv('INSTA_LOGIN'), os.getenv('INSTA_PWD')))
    crawler_proc.start()