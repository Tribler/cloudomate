# -*- coding: utf-8 -*-
import logging

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from scrapy.utils.response import open_in_browser

from util.config import read_config
from vps.vpsoption import VpsOption


class RamnodeSpider(scrapy.Spider):
    name = "ramnode"
    start_urls = [
        'https://ramnode.com/vps.php',
    ]
    config = read_config()

    def __init__(self, **kwargs):
        super(RamnodeSpider, self).__init__(**kwargs)

    def parse(self, response):
        yield scrapy.Request('https://clientarea.ramnode.com/cart.php?a=add&pid=206', callback=self.checkout)
        pass

    def checkout(self, response):
        yield scrapy.FormRequest(url="https://clientarea.ramnode.com/cart.php",
                                 formdata=
                                 {'ajax': '1',
                                  'a': 'confproduct',
                                  'configure': 'true',
                                  'i': '0',
                                  'billingcycle': 'monthly',
                                  'hostname': 'asdf',
                                  'ns1prefix': self.config.get("server", "ns1"),
                                  'ns2prefix': self.config.get("server", "ns2"),
                                  'rootpw': 'auto-generated',
                                  'configoption[135]': '1370',
                                  'configoption[136]': '1377', },
                                 callback=self.after_post)

    def after_post(self, response):
        yield scrapy.Request('https://clientarea.ramnode.com/cart.php?a=confdomains', callback=self.review)

    def review(self, response):
        token = response.css("input[name=token]::attr(value)").extract_first()
        logging.log(logging.INFO, "Token " + token)
        yield scrapy.FormRequest(url="https://clientarea.ramnode.com/cart.php?a=checkout&submit=true&submit=true",
                                 formdata=
                                 {'token': token,
                                  'custtype': 'new',
                                  'loginemail': '',
                                  'loginpw': '',
                                  'firstname': self.config.get("user", "firstName"),
                                  'address1': self.config.get("address", "address"),
                                  'lastname': self.config.get("user", "lastName"),
                                  'address2': '',
                                  'companyname': self.config.get("user", "companyName"),
                                  'city': self.config.get("address", "city"),
                                  'email': self.config.get("user", "email"),
                                  'state': 'Alabama',
                                  'password': self.config.get("user", "password"),
                                  'postcode': self.config.get("address", "zipcode"),
                                  'password2': self.config.get("user", "passwrod"),
                                  'country': self.config.get("user", "countryCode"),
                                  'phonenumber': self.config.get("user", "phoneNumber"),
                                  'securityqid': '1',
                                  'securityqans': self.config.get("user", "password"),
                                  'customfield[321]': '',
                                  'customfield[1767]': '',
                                  'promocode': '',
                                  'notes': '',
                                  'paymentmethod': 'bitpay',
                                  'ccinfo': 'new',
                                  'ccexpirymonth': '01',
                                  'ccexpiryyear': '2017',
                                  'cccvv': '123',
                                  'accepttos': 'on', }
                                 , callback=self.after_review)

    def after_review(self, response):
        open_in_browser(response)


class RamnodeOptions(scrapy.Spider):
    def __init__(self, **kwargs):
        super(RamnodeOptions, self).__init__(**kwargs)

    name = "ramnode_options"
    start_urls = [
        'https://ramnode.com/vps.php',
    ]

    def parse(self, response):
        # il = ItemLoader(item=VpsOption, response=response)
        rows = response.xpath(
            "//table[@class='table table-striped table-centered']/tbody/tr")
        for t in rows:
            yield self.parse_item(t)
        pass

    @staticmethod
    def parse_item(item):
        il = OptionLoader(item=VpsOption(), selector=item)
        il.add_xpath('name', 'td[1]/strong/text()')
        il.add_xpath('ram', 'td[2]/text()')
        il.add_xpath('cpu', 'td[3]/text()')
        il.add_xpath('ipv4', 'td[4]/text()')
        il.add_xpath('storage', 'td[6]/text()')
        il.add_xpath('bandwidth', 'td[7]/text()')
        il.add_xpath('price', 'td[8]/strong/text()')
        i = il.load_item()
        return i


class OptionLoader(ItemLoader):
    default_output_processor = TakeFirst()
