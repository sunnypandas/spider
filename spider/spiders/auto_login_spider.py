# -*- coding: utf-8 -*-
import base64
import datetime
import re
import urllib

import requests
import scrapy
from scrapy.spiders.init import InitSpider
from scrapy import Selector, Request
from autologin import AutoLogin
from inline_requests import inline_requests
# from scrapy_splash import SplashRequest

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MYSQL_ITEM_PIPELINES

class AutoLoginSpider(InitSpider):
    name = "auto_login"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF,
        # 'DOWNLOAD_DELAY': 3
    }
    allowed_domains = ['iresearch.cn']
    batch = datetime.datetime.now().date()
    default_data = {

    }
    default_headers = {

    }

    def init_request(self):
        """This function is called before crawling starts."""
        self.logger.info("Start a login page.")
        return scrapy.Request(url='http://center.iresearch.cn/ajax/process.ashx?work=login&uAccount=&uPassword=&days=15&t=0.46381088452849806', callback=self.check_login_response)

    def login(self, response):
        """Generate a login request."""
        self.logger.info("Generate a login request.")
        return scrapy.FormRequest.from_response(response,
                                         formdata={'work': 'login', 'uAccount': '', 'uPassword': '', 'days': '15', 't': '0.46381088452849806'},
                                         callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are successfully logged in."""
        result = response.text
        if result == '1':
            self.logger.info("Successfully logged in. Let's start crawling!")
            # Now the crawling can begin..
            yield scrapy.Request(url='http://report.iresearch.cn/', callback=self.parse_basic_info, headers=response.headers)
            # yield SplashRequest(url='http://www.iresearch.cn/include/auto/wxpro.ashx?work=get&url=http%3A%2F%2Freport.iresearch.cn%2F',
            #                      headers= response.headers, callback=self.double_request, dont_filter=True)
            return self.initialized()
        else:
            self.logger.info("Login failed!")

    def parse_basic_info(self, response):
        basic_info = response.text
        items = Selector(text=basic_info).xpath('//ul[@id="ulroot3"]/li').extract()
        for item in items:
            url = Selector(text=item).xpath('//div[@class="u-img"]/a/@href').extract()[0]
            title = Selector(text=item).xpath('//div[@class="txt"]/h3/a/text()').extract()[0]
            content = Selector(text=item).xpath('//div[@class="txt"]/p/text()').extract()[0]
            cover = base64.b64encode(
                requests.get(Selector(text=item).xpath('//div[@class="u-img"]/a/img/@src').extract()[0]).content,)
            keywords = ''
            if len(Selector(text=item).xpath(
                    '//div[@class="txt"]/div[@class="foot f-cb"]/div[@class="link f-fl"]/a/text()').extract()) > 0:
                keywords = ','.join(Selector(text=item).xpath(
                    '//div[@class="txt"]/div[@class="foot f-cb"]/div[@class="link f-fl"]/a/text()').extract())
            hot = '2'
            type = '行业报告'
            update = Selector(text=item).xpath(
                '//div[@class="txt"]/div[@class="foot f-cb"]/div[@class="time f-fr"]/span/text()').extract()[0]
            yield scrapy.Request(url=url, headers=self.default_headers,
                                 meta={'title': title, 'content': content, 'cover': cover, 'keywords': keywords,
                                       'hot': hot, 'type': type, 'update': update},
                                 callback=self.parse_detail_info, dont_filter=True)

    @inline_requests
    def parse_detail_info(self, response):
        detail_info = response.text
        url = response.url
        title = response.meta['title']
        content = response.meta['content']
        pattern = re.compile('</?a[^>]*>')
        content = pattern.sub('', content)
        pattern = re.compile('</?img[^>]*>')
        content = pattern.sub('', content)
        cover = response.meta['cover']
        pdf = ''
        pdf_price = Selector(text=detail_info).xpath('//li[@class="price"]/text()').extract()[0]
        pdf_url = 'http://report.iresearch.cn/include/ajax/user_ajax.ashx?reportid=' + str(url[url.rfind('/') + 1:-6]) + '&work=rdown&url=' + url
        if '￥0' == pdf_price:
            pdf = yield Request(
                url=pdf_url,
            )
            self.save_pdf(pdf)
        keywords = response.meta['keywords']
        hot = response.meta['hot']
        type = response.meta['type']
        update = response.meta['update']
        batch = self.batch
        table_name = 'spider.news'

    def save_pdf(self, response):
        path = response.url.split('/')[-1][0:-5] + 'pdf'
        self.logger.info('Saving PDF %s', path)
        # with open(path, 'wb') as f:
        #     f.write(response.body)