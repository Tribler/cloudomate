from hoster import Hoster
from scrapy.crawler import CrawlerProcess
import json

'''
ScrapyHoster provides a common implementation for all hosts accessible through scrapy only.
'''

CONFIG_PATH_STRING = '.vpsconfigs/{0}.json'

class ScrapyHoster(Hoster):
    def __init__(self, name, options_spider, spider):
        self.options_spider = options_spider
        self.spider = spider
        self.configurations = None
        self.name = name

    def options(self):
        if not self.configurations:
            process = CrawlerProcess({
                'ITEM_PIPELINES': {'vps.scrapy_hoster.MyPipeline': 1},
                'hoster_name': self.name
            })
            process.crawl(self.options_spider)
            process.start()

        with open(CONFIG_PATH_STRING.format(self.name), 'rb') as f:
            self.configurations = json.load(f)

        return self.configurations

    def get_configurations(self):
        return self.configurations

    def add_configuration(self, configuration):
        if not self.configurations_crawled:
            self.configurations.append(configuration)

from scrapy import signals
from scrapy.exporters import JsonItemExporter

class MyPipeline(object):
    def __init__(self, hoster_name):
        self.hoster_name = hoster_name
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(hoster_name=crawler.settings.get('hoster_name'))
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file = open(CONFIG_PATH_STRING.format(self.hoster_name), 'wb')
        self.files[spider] = file
        self.exporter = JsonItemExporter(file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

