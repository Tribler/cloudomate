"""
ScrapyHoster provides a common implementation for all hosts accessible through scrapy only.
"""
import json

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.exporters import JsonItemExporter

from hoster import Hoster

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

    def print_configurations(self):
        row_format = "{:<5}" + "{:15}" * 6
        print(row_format.format("#", "Name", "CPU", "RAM", "Storage", "Bandwidth", "Price"))

        i = 0
        for item in self.configurations:
            print(row_format.format(str(i) + ":", item["name"], item["cpu"], item["ram"], item["storage"],
                                    item["bandwidth"], item["price"]))
            i = i + 1


class MyPipeline(object):
    def __init__(self, hoster_name):
        self.hoster_name = hoster_name
        self.files = {}
        self.exporter = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(hoster_name=crawler.settings.get('hoster_name'))
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        spider_file = open(CONFIG_PATH_STRING.format(self.hoster_name), 'wb')
        self.files[spider] = spider_file
        self.exporter = JsonItemExporter(spider_file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        spider_file = self.files.pop(spider)
        spider_file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
