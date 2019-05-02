# -*- coding: utf-8 -*-
import urllib

import scrapy
from scrapy.selector import Selector

from spider.consts import MYSQL_ITEM_PIPELINES, DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
from spider.items import SpiderLoaderItem, BankListItem


class WikiBankSpider(scrapy.Spider):
    name = "wikibank"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
    }
    allowed_domains = ['zh.wikipedia.org']
    def start_requests(self):
        default_data = {
        }
        default_headers = {
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Upgrade-Insecure-Requests': 1,
            'Connection': 'keep-alive',
            'Host': 'zh.wikipedia.org'
        }
        default_data = urllib.parse.urlencode(default_data)
        yield scrapy.Request(
            url='https://zh.wikipedia.org/wiki/%E4%B8%AD%E5%9B%BD%E5%A4%A7%E9%99%86%E9%93%B6%E8%A1%8C%E5%88%97%E8%A1%A8',
            headers=default_headers, body=default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        #中央银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E4.B8.AD.E5.A4.AE.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::table[1]//tr').extract()
        basic_info.pop(0)
        print('======================中央银行======================')
        for info in basic_info:
            name=Selector(text=info).xpath('//td[1]/a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '中央银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info=[]
        print('**********************中央银行**********************')

        # 政策性银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E6.94.BF.E7.AD.96.E6.80.A7.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::table[1]//tr').extract()
        basic_info.pop(0)
        print('======================政策性银行======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//td[1]/a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '政策性银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************政策性银行**********************')

        # 大型商业银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E5.A4.A7.E5.9E.8B.E5.95.86.E4.B8.9A.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::table[1]//tr').extract()
        basic_info.pop(0)
        print('======================大型商业银行======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//td[1]/a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '大型商业银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************大型商业银行**********************')

        # 邮政储蓄银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E9.82.AE.E6.94.BF.E5.82.A8.E8.93.84.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::table[1]//tr').extract()
        basic_info.pop(0)
        print('======================邮政储蓄银行======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//td[1]/a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '邮政储蓄银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************邮政储蓄银行**********************')

        # 股份制商业银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E8.82.A1.E4.BB.BD.E5.88.B6.E5.95.86.E4.B8.9A.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::table[1]//tr').extract()
        basic_info.pop(0)
        print('======================股份制商业银行======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//td[1]/a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '股份制商业银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************股份制商业银行**********************')

        # 城市商业银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E5.9F.8E.E5.B8.82.E5.95.86.E4.B8.9A.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::table[1]//tr').extract()
        basic_info.pop(0)
        print('======================城市商业银行======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//td[1]/a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '城市商业银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************城市商业银行**********************')

        # 民营银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E6.B0.91.E8.90.A5.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::table[1]//tr').extract()
        basic_info.pop(0)
        print('======================民营银行======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//td[1]/a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '民营银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************民营银行**********************')

        # 直销银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E7.9B.B4.E9.94.80.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::table[1]//tr').extract()
        basic_info.pop(0)
        print('======================直销银行======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//td[1]/a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '直销银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************直销银行**********************')

        # 农村商业银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E5.86.9C.E6.9D.91.E5.95.86.E4.B8.9A.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::p[1]//a').extract()
        print('======================农村商业银行======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '农村商业银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************农村商业银行**********************')

        # 农村信用联合社
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E5.86.9C.E6.9D.91.E4.BF.A1.E7.94.A8.E8.81.94.E5.90.88.E7.A4.BE"]/parent::h2/following-sibling::p[1]//a').extract()
        print('======================农村信用联合社======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '农村信用联合社')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************农村信用联合社**********************')

        # 村镇银行、贷款公司和农村资金互助社
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E6.9D.91.E9.95.87.E9.93.B6.E8.A1.8C.E3.80.81.E8.B4.B7.E6.AC.BE.E5.85.AC.E5.8F.B8.E5.92.8C.E5.86.9C.E6.9D.91.E8.B5.84.E9.87.91.E4.BA.92.E5.8A.A9.E7.A4.BE"]/parent::h2/following-sibling::p[1]//a').extract()
        print('======================村镇银行、贷款公司和农村资金互助社======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '村镇银行、贷款公司和农村资金互助社')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        extra_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E6.9D.91.E9.95.87.E9.93.B6.E8.A1.8C.E3.80.81.E8.B4.B7.E6.AC.BE.E5.85.AC.E5.8F.B8.E5.92.8C.E5.86.9C.E6.9D.91.E8.B5.84.E9.87.91.E4.BA.92.E5.8A.A9.E7.A4.BE"]/parent::h2/following-sibling::p[1]/text()').extract()[-1]
        for info in extra_info.split():
            name=info
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '村镇银行、贷款公司和农村资金互助社')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        print('**********************村镇银行、贷款公司和农村资金互助社**********************')

        # 外资银行
        basic_info = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]//span[@id=".E5.A4.96.E8.B5.84.E9.93.B6.E8.A1.8C"]/parent::h2/following-sibling::p[1]//a').extract()
        print('======================外资银行======================')
        for info in basic_info:
            name = Selector(text=info).xpath('//a/text()').extract()[0]
            item = SpiderLoaderItem(item=BankListItem(), response=response)
            item.add_value('type', '外资银行')
            item.add_value('name', name)
            item.add_value('url', '')
            item.add_value('longitude', '')
            item.add_value('latitude', '')
            item.add_value('address', '')
            item.add_value('tel', '')
            item.add_value('workday', '')
            item.add_value('table_name', 'DATAMINING.WIKI_BANK_LIST')
            yield item.load_item()
        basic_info = []
        print('**********************外资银行**********************')

    def closed(self, reason):
        '''
        爬虫结束时退出登录状态
        :param reason:
        :return:
        '''
        if 'finished' == reason:
            self.logger.warning('%s', '爬虫程序执行结束，即将关闭')
        elif 'shutdown' == reason:
            self.logger.warning('%s', '爬虫进程被强制中断，即将关闭')
        elif 'cancelled' == reason:
            self.logger.warning('%s', '爬虫被引擎中断，即将关闭')
        else:
            self.logger.warning('%s', '爬虫被未知原因打断，即将关闭')