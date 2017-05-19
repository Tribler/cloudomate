"""
ScrapyHoster provides a common implementation for all hosts accessible through scrapy only.
"""
import json
from collections import OrderedDict

from appdirs import *
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.exporters import JsonItemExporter
from twisted.internet import reactor

from cloudomate.vps.hoster import Hoster

CACHE_DIRECTORY = user_cache_dir('cloudomate')
CONFIG_PATH_STRING = os.path.join(CACHE_DIRECTORY, '{0}.json')


class ScrapyHoster(Hoster):
    def __init__(self, name, options_spider, spider):
        self.options_spider = options_spider
        self.spider = spider
        self.configurations = None
        self.name = name

    def options(self):
        if not self.configurations:
            process = CrawlerProcess({
                'ITEM_PIPELINES': {'cloudomate.vps.scrapy_hoster.MyPipeline': 1},
                'hoster_name': self.name
            })
            process.crawl(self.options_spider)
            d = process.join()
            d.addBoth(self.stop)
            process.start(stop_after_crawl=False)

        with open(CONFIG_PATH_STRING.format(self.name), 'rb') as f:
            self.configurations = json.load(f)

        return self.configurations

    def stop(self, a):
        reactor.stop()
        pass
        # reactor.stop()

    def get_configurations(self):
        return self.configurations

    def print_configurations(self):
        """
        Print parsed VPS configurations.
        """
        item_names = OrderedDict([
            ("name", "Name"),
            ("cpu", "CPU"),
            ("ram", "RAM"),
            ("storage", "Storage"),
            ("bandwidth", "Bandwidth"),
            ("connection", "Connection"),
            ("price", "Price"),
        ])
        row_format = "{:<5}" + "{:15}" * len(item_names)
        values = ["#"] + item_names.values()
        print(row_format.format(*values))

        i = 0
        for item in self.configurations:
            self._print_row(i, item, item_names)
            i = i + 1

    @staticmethod
    def _print_row(i, item, item_names):
        row_format = "{:<5}" + "{:15}" * len(item_names)
        values = [i]
        for key in item_names.keys():
            if key in item:
                values.append(item[key])
            else:
                values.append("")
        print(row_format.format(*values))

    def register(self, configuration):
        process = CrawlerProcess({
            'ITEM_PIPELINES': {'cloudomate.vps.scrapy_hoster.MyPipeline': 1},
            'hoster_name': self.name,
            'configuration': configuration
        })
        process.crawl(self.spider)
        process.start()


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
        if not os.path.exists(CACHE_DIRECTORY):
            os.makedirs(CACHE_DIRECTORY)
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
