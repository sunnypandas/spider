# -*- coding: utf-8 -*-
import base64
import datetime
import math
import urllib

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, ProxyListItem
from spider.utils.mysqlutils import Mysql


class FreeSpider(scrapy.Spider):
    name = "free-proxy"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
    }
    allowed_domains = ['free-proxy.cz']
    batch_date = datetime.datetime.now().date()
    default_data = {
    }
    default_data = urllib.parse.urlencode(default_data)
    #default_data = json.dumps(default_data)
    default_headers = {
        # 'Content-Length':'2',
        'Accept-Language':' ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5,zh-TW;q=0.4',
        'Proxy-Connection':' keep-alive',
        'Accept':' text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent':' Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Host':' free-proxy.cz',
        'Cookie':' __utmc=104525399; __utmz=104525399.1522538151.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); fp=2b0959527ef458f0a752501c8ddbe8f5; __utma=104525399.1106036388.1522538151.1522538151.1522545178.2; __utmt=1; __utmb=104525399.8.10.1522545181',
        'Upgrade-Insecure-Requests':'1',
        'Accept-Encoding':' gzip, deflate'

    }
    def start_requests(self):
        Mysql().delete("delete from proxy_list_all")
        yield scrapy.Request(
            url='http://free-proxy.cz/zh/proxylist/main/1',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        total_page = response.xpath('//div[@id="search"]/following-sibling::h1/text()').extract()[0]
        start = '目前只有 '
        end = ' 个代理'
        pages = int(math.ceil(int((total_page.split(start))[1].split(end)[0])/30.0))
        for page in range(1, pages + 1):
            # time.sleep(random.uniform(3, 5))
            yield scrapy.Request(
                url='http://free-proxy.cz/zh/proxylist/main/'+str(page),
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)
    def parse_basic_info(self, response):
        contents=response.xpath('//table[@id="proxy_list"]/tbody//tr').extract()
        for content in contents:
            if len(Selector(text=content).xpath('//tr//td').extract())>1:
                coded_string=''
                ip=''
                if len(Selector(text=content).xpath('//tr//td[1]/script/text()').extract())>0:
                    coded_string = Selector(text=content).xpath('//tr//td[1]/script/text()').extract()[0][30:-3]
                else:
                    coded_string = Selector(text=content).xpath('//tr//td[1]/abbr/script/text()').extract()[0][30:-3]
                if coded_string != '':
                    ip = self.decode_base64(coded_string)
                port=Selector(text=content).xpath('//tr//td[2]/span/text()').extract()[0]
                proxy = Selector(text=content).xpath('//tr//td[3]/small/text()').extract()[0]
                anonymous = Selector(text=content).xpath('//tr//td[7]/small/text()').extract()[0]
                item = SpiderLoaderItem(item=ProxyListItem(), response=response)
                item.add_value('batch_date', self.batch_date)
                item.add_value('ip', ip)
                item.add_value('port', port)
                item.add_value('proxy', proxy)
                item.add_value('anonymous', anonymous)
                item.add_value('table_name', 'proxy_list_all')
                yield item.load_item()

    def decode_base64(self,data):
        missing_padding = len(data) % 4
        if missing_padding != 0:
            data += b'=' * (4 - missing_padding)
        return base64.decodestring(data)

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