# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy import Selector

from spider.consts import MYSQL_ITEM_PIPELINES, DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
from spider.items import SpiderLoaderItem, AnimationBangumiItem, AnimationEpisodeItem


class FengchedmSpider(scrapy.Spider):
    name = "fengchedm"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
    }
    allowed_domains = ['www.fengchedm.com']
    batch_date = datetime.datetime.now().date()
    default_data = {
    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'DNT': '1',
        'Host': 'www.fengchedm.com',
        'Proxy-Connection': 'Keep-Alive'
    }
    def start_requests(self):
        yield scrapy.Request(
            url='http://www.fengchedm.com/type1/0-0-0-0-1.html',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url,dont_filter=True)
    def get_final_url(self, response):
        total_page = response.xpath('//div[@class="fire l"]/div[@class="pages"]/div[@class="pages"]/text()').extract()[2][1:-1]
        pages = int(total_page)
        for page in range(1,pages+1):
            #time.sleep(random.uniform(1, 3))
            url='http://www.fengchedm.com/type1/0-0-0-0-'+str(page)+'.html'
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="fire l"]/div[@class="pics"]/ul//li').extract()
        for content in contents:
            url='http://www.fengchedm.com'+Selector(text=content).xpath('//li[1]/a[1]/@href').extract()[0]
            img = Selector(text=content).xpath('//li[1]/a[1]/img/@src').extract()[0]
            name = Selector(text=content).xpath('//li[1]/a[1]/img/@alt').extract()[0]
            update_time = Selector(text=content).xpath('//li[1]/span[2]/font/text()').extract()[0]
            yield scrapy.Request(
               url=url,
               headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, meta={'img': img, 'name': name, 'update_time': update_time}, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        img = response.meta['img']
        name = response.meta['name']
        update_time = response.meta['update_time']
        content = response.xpath('//div[@class="fire l"]/div[@class="intro r"]/div[@class="alex"]').extract()[0]
        status = Selector(text=content).xpath('//div[@class="alex"]/span[2]/text()').extract()[0][3:]+Selector(text=content).xpath('//div[@class="alex"]/span[1]/text()').extract()[0][3:]
        author_names=Selector(text=content).xpath('//div[@class="alex"]/span[3]/text()').extract()[0][3:]
        type = Selector(text=content).xpath('//div[@class="alex"]/span[4]/text()').extract()[0][3:]
        area_names = Selector(text=content).xpath('//div[@class="alex"]/span[5]/text()').extract()[0][3:]
        introduction = response.xpath('//div[@class="info"]').extract()[0]
        item_bangumi = SpiderLoaderItem(item=AnimationBangumiItem(image_urls=[img]), response=response)
        item_bangumi.add_value('batch_date', self.batch_date)
        item_bangumi.add_value('host', self.allowed_domains[0])
        item_bangumi.add_value('url', url)
        item_bangumi.add_value('img', img)
        item_bangumi.add_value('name', name)
        item_bangumi.add_value('author_names', author_names)
        item_bangumi.add_value('area_names', area_names)
        item_bangumi.add_value('status', status)
        item_bangumi.add_value('type', type)
        item_bangumi.add_value('introduction', introduction)
        item_bangumi.add_value('update_time', update_time)
        item_bangumi.add_value('table_name', 'animation_bangumi')
        yield item_bangumi.load_item()

        episodes = response.xpath('//div[@class="fire l"]/div[@class="tabs"]').extract()[0]
        playee_names=Selector(text=episodes).xpath('//div[@class="tabs"]/ul[@class="menu0"]').extract()
        episodess = Selector(text=episodes).xpath('//div[@class="tabs"]/div[@class="main0"]').extract()
        episode_size=len(playee_names)
        for idx in range(0,episode_size):
            playee_name = None
            if len(Selector(text=playee_names[idx]).xpath('//ul[@class="menu0"]/li[@class="on"]/strong').extract())>0:
                playee_name=Selector(text=playee_names[idx]).xpath('//ul[@class="menu0"]/li[@class="on"]/strong/text()').extract()[0]
            else:
                playee_name = Selector(text=playee_names[idx]).xpath('//ul[@class="menu0"]/li[@class="on"]/text()').extract()[0]
            episodes = Selector(text=episodess[idx]).xpath('//div[@class="main0"]/div[@class="movurl"]/ul//li').extract()
            for episode in episodes:
                episode_name=Selector(text=episode).xpath('//li/a/text()').extract()[0]
                episode_url = 'http://www.fengchedm.com'+Selector(text=episode).xpath('//li/a/@href').extract()[0]
                item_episode = SpiderLoaderItem(item=AnimationEpisodeItem(), response=response)
                item_episode.add_value('batch_date', self.batch_date)
                item_episode.add_value('bangumi_url', url)
                item_episode.add_value('episode_name', episode_name)
                item_episode.add_value('episode_url', episode_url)
                item_episode.add_value('playee_name', playee_name)
                item_episode.add_value('table_name', 'animation_episode')
                yield item_episode.load_item()

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