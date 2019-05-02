# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, \
    MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, AnimationEpisodeItem, AnimationBangumiItem


class Aidm5Spider(scrapy.Spider):
    name = "5aidm"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
    }
    allowed_domains = ['www.5aidm.com']
    batch_date = datetime.datetime.now().date()
    default_data = {
    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
    }
    def start_requests(self):
        yield scrapy.Request(
            url='https://www.5aidm.com/',
            headers=self.default_headers, body=self.default_data, callback=self.get_type_url, dont_filter=True)
    def get_type_url(self, response):
        urls = response.xpath('//div[@class="dh2"]//div[@class="dh2_z"]//a/@href').extract()
        for url in urls:
            yield scrapy.Request(
                url='https://www.5aidm.com'+url,
                headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        total_page = response.xpath('//div[@class="index_z"]//div[@class="piclist"]//div[@class="page"]/span[1]/text()').extract()[0]
        pages = int(total_page.split('/')[1][0:-1])
        for page in range(1, pages + 1):
            # time.sleep(random.uniform(3, 5))
            url=None
            if page==1:
                url=response.url
            else:
                url = response.url[0:-4]+'-'+str(page)+'.htm'
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)
    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="index_z"]/div[@class="piclist"]/ul[1]//li').extract()
        for content in contents:
            url = 'https://www.5aidm.com'+Selector(text=content).xpath('//li[@class="hw"]/a/@href').extract()[0]
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        content = response.xpath('//div[@class="content_info"]').extract()[0]
        introduction = response.xpath('//div[@class="Content_des"]').extract()[0]
        img = Selector(text=content).xpath('//div[@class="content_info"]/div[@class="content_pic"]/img/@src').extract()[0]
        name = Selector(text=content).xpath('//div[@class="content_info"]/div[@class="content_pic"]/img/@alt').extract()[0]
        status=None
        if len(Selector(text=content).xpath('//div[@class="content_info"]/div[@class="content_d"]//li[@class="w1"][1]/span/font/text()').extract())>0:
            status = Selector(text=content).xpath('//div[@class="content_info"]/div[@class="content_d"]//li[@class="w1"][1]/span/font/text()').extract()[0]
        author_names = Selector(text=content).xpath('//div[@class="content_info"]/div[@class="content_d"]//li[@class="w1"][3]/text()').extract()[0][5:]
        area_names = Selector(text=content).xpath('//div[@class="content_info"]/div[@class="content_d"]//li[@class="w1"][4]/text()').extract()[0][5:]
        show_date=Selector(text=content).xpath('//div[@class="content_info"]/div[@class="content_d"]//li[@class="w1"][5]/text()').extract()[0][5:]
        update_time = Selector(text=content).xpath('//div[@class="content_info"]/div[@class="content_d"]//li[@class="w1"][6]/text()').extract()[0][5:]
        item = SpiderLoaderItem(item=AnimationBangumiItem(image_urls=[img]), response=response)
        item.add_value('batch_date', self.batch_date)
        item.add_value('host', self.allowed_domains[0])
        item.add_value('url', url)
        item.add_value('img', img)
        item.add_value('name', name)
        item.add_value('author_names', author_names)
        item.add_value('show_date', show_date)
        item.add_value('area_names', area_names)
        item.add_value('status', status)
        item.add_value('introduction', introduction)
        item.add_value('update_time', update_time)
        item.add_value('table_name', 'animation_bangumi')
        yield item.load_item()
        if len(response.xpath('//div[@class="content_z"]//div[@class="downlist"]').extract())>0:
            episodes_info=response.xpath('//div[@class="content_z"]//div[@class="downlist"]').extract()
            for episode_info in episodes_info:
                playee_name=Selector(text=episode_info).xpath('//div[@class="downlist"]/p//span/text()').extract()[0]
                download_url_list = Selector(text=episode_info).xpath('//div[@class="downlist"]/ul//li').extract()
                for download_url in download_url_list:
                    episode_name=Selector(text=download_url).xpath('//li/a/@title').extract()[0]
                    episode_url = 'https://www.5aidm.com'+Selector(text=download_url).xpath('//li/a/@href').extract()[0]
                    yield scrapy.Request(
                        url=episode_url,
                        headers=self.default_headers, body=self.default_data, meta={'bangumi_url': url,'episode_name': episode_name,'playee_name': playee_name},
                        callback=self.parse_episode_info, dont_filter=True)

    def parse_episode_info(self, response):
        bangumi_url = response.meta['bangumi_url']
        episode_name = response.meta['episode_name']
        episode_url=response.url
        playee_name = response.meta['playee_name']
        playee_url = response.xpath('//div[@class="content_z"]/div[@class="down_d"]/div[@class="down_d_y"]/a[1]/@href').extract()[0]
        item = SpiderLoaderItem(item=AnimationEpisodeItem(), response=response)
        item.add_value('batch_date', self.batch_date)
        item.add_value('bangumi_url', bangumi_url)
        item.add_value('episode_name', episode_name)
        item.add_value('episode_url', episode_url)
        item.add_value('playee_name', playee_name)
        item.add_value('playee_url', playee_url)
        item.add_value('table_name', 'animation_episode')
        yield item.load_item()

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
