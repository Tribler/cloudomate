from hoster import Hoster
from scrapy.crawler import CrawlerProcess

'''
ScrapyHoster provides a common implementation for all hosts accessible through scrapy only.
'''
class ScrapyHoster(Hoster):
    def __init__(self, options_spider, spider):
        self.options_spider = options_spider
        self.spider = spider
        self.configurations_crawled = False
        self.configurations = None
        self.testname='testname'

    def options(self):
        if not self.configurations:
            self.configurations = []
            process = CrawlerProcess({
                'ITEM_PIPELINES': {'vps.scrapy_hoster.MyPipeline': 1},
                'scrapy_hoster_object': self
            })
            process.crawl(self.options_spider)
            process.start()
            self.configurations_crawled = True
        return self.configurations

    def get_configurations(self):
        return self.configurations

    def add_configuration(self, configuration):
        if not self.configurations_crawled:
            self.configurations.append(configuration)


class MyPipeline(object):
    def __init__(self, hoster_object):
        self.hoster_object = hoster_object
        print(hoster_object.testname)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            hoster_object=crawler.settings.get('scrapy_hoster_object')
        )

    def process_item(self, item, spider):
        print('processing item'.format(self.hoster_object.testname))
        self.hoster_object.add_configuration((item["name"], item["cpu"], item["ram"], item["storage"]))

