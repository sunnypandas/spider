# -*- coding: utf-8 -*-
import urllib

import scrapy
from scrapy.selector import Selector

from spider.consts import MYSQL_ITEM_PIPELINES, DOWNLOADER_MIDDLEWARES_HTTP_PROXY_ON
from spider.items import BankListItem, SpiderLoaderItem


class CbrcBankSpider(scrapy.Spider):
    name = "cbrcbank"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_ON
    }
    allowed_domains = ['www.cbrc.gov.cn']
    def start_requests(self):
        default_data = {
        }
        default_headers = {
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': 1,
            'Connection': 'keep-alive',
            'Host': 'www.cbrc.gov.cn'
        }
        default_data = urllib.parse.urlencode(default_data)
        yield scrapy.Request(
            url='http://www.cbrc.gov.cn/chinese/jrjg/index.html',
            headers=default_headers, body=default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        basic_info = response.xpath('//div[@class="zong"]//div[@class="wai"]').extract()
        id=2
        for info in basic_info:
            type = Selector(text=info).xpath('//div[@class="zi"]/text()').extract()[0]
            type=type.strip()
            name_info = Selector(text=info).xpath('//div[@id="b '+str(id)+'"]/ul/li/ul/li').extract()
            id=id+1
            for fake_name in name_info:
                name = None
                url = None
                has_a = Selector(text=fake_name).xpath('//li/a').extract()
                if len(has_a) == 0:
                    name = Selector(text=fake_name).xpath('//li/text()').extract()[0]
                    url = None
                else:
                    name = Selector(text=fake_name).xpath('//li/a/text()').extract()[0]
                    url = Selector(text=fake_name).xpath('//li/a/@href').extract()[0]
                if name != None:
                    name = name.strip()
                if url != None:
                    url = url.strip()
                    if len(url) <= 7:
                        url = None
                item = SpiderLoaderItem(item=BankListItem(), response=response)
                item.add_value('type', type)
                item.add_value('name', name)
                item.add_value('url', url)
                item.add_value('longitude', '')
                item.add_value('latitude', '')
                item.add_value('address', '')
                item.add_value('tel', '')
                item.add_value('workday', '')
                item.add_value('table_name', 'CBRCBANK_BANK_LIST')
                yield item.load_item()
