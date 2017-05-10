import scrapy


class VpsOption(scrapy.Item):
    name = scrapy.Field()
    virtualization = scrapy.Field()
    ram = scrapy.Field()
    cpu = scrapy.Field()
    ipv4 = scrapy.Field()
    storage = scrapy.Field()
    storage_type = scrapy.Field()
    bandwidth = scrapy.Field()
    price = scrapy.Field()
    location = scrapy.Field()
