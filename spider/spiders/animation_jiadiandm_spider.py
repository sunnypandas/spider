# -*- coding: utf-8 -*-
import datetime
import json

import scrapy
from scrapy import Selector

from spider.consts import MYSQL_ITEM_PIPELINES, DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
from spider.items import SpiderLoaderItem, AnimationBangumiItem, AnimationEpisodeItem


class JiadiandmSpider(scrapy.Spider):
    name = "jiadiandm"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
    }
    allowed_domains = ['www.jiadiandm.com']
    batch_date = datetime.datetime.now().date()
    default_data = {
    }
    #default_data = urllib.parse.urlencode(default_data)
    default_data = json.dumps(default_data)
    default_headers = {
        'Cache-Control': 'max-age=0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5',
        #'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
        'Referer': 'https://www.jiadiandm.com/rhdm/',
        'Upgrade-Insecure-Requests': 1,
        'Connection': 'keep-alive',
        'Host': 'www.jiadiandm.com'
    }
    def start_requests(self):
        yield scrapy.Request(
            url='https://www.jiadiandm.com/search.php?searchtype=5',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url,dont_filter=True)
    def get_final_url(self, response):
        total_page = response.xpath('//div[@class="wrap mb "]/div[@class="list_z2 g3"]/div[@class="pagetop2 pslpx"]/div[@class="page"]//span[1]/text()').extract()[0]
        pages = int(total_page.split('/')[1].split(' ')[0])
        for page in range(1,pages+1):
            #time.sleep(random.uniform(1, 3))
            url='https://www.jiadiandm.com/search.php?page='+str(page)+'&searchtype=5'
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="wrap mb "]/div[@class="list_z2 g3"]/div[@class="list_z g4 pslpx"]/ul[@class="ipic"]//li').extract()
        for content in contents:
            url='https://www.jiadiandm.com'+Selector(text=content).xpath('//li[1]/a/@href').extract()[0]
            img = Selector(text=content).xpath('//li/a/img/@src').extract()[0]
            if img!=None and img!='' and (not img.startswith('http')):
                img='https://www.jiadiandm.com'+img
            name = Selector(text=content).xpath('//li/a/img/@alt').extract()[0]
            status=None
            if len(Selector(text=content).xpath('//li/a/span/text()').extract())>0:
                status = Selector(text=content).xpath('//li/a/span/text()').extract()[0]
            yield scrapy.Request(
               url=url,
               headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, meta={'img': img, 'name': name, 'status': status}, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        img = response.meta['img']
        name = response.meta['name']
        status = response.meta['status']
        content = response.xpath('//div[@class="wrap mb"]/div[@class="Content_z g6 pslpx"]/div[@class="Content"]/p[@class="w2"]').extract()
        area_names = Selector(text=content[0]).xpath('//p[@class="w2"]/text()').extract()[0].strip()[1:]
        language = Selector(text=content[1]).xpath('//p[@class="w2"]/text()').extract()[0].strip()[1:]
        show_date = Selector(text=content[1]).xpath('//p[@class="w2"]/text()').extract()[1].strip()[1:]
        author_names=Selector(text=content[2]).xpath('//p[@class="w2"]/text()').extract()[0].strip()[1:]
        update_time = Selector(text=content[4]).xpath('//p[@class="w2"]/text()').extract()[0].strip()[1:]
        introduction = response.xpath('//div[@class="Content_des pslpx"]').extract()[0]
        item_bangumi = SpiderLoaderItem(item=AnimationBangumiItem(image_urls=[img]), response=response)
        item_bangumi.add_value('batch_date', self.batch_date)
        item_bangumi.add_value('host', self.allowed_domains[0])
        item_bangumi.add_value('url', url)
        item_bangumi.add_value('img', img)
        item_bangumi.add_value('name', name)
        item_bangumi.add_value('author_names', author_names)
        item_bangumi.add_value('show_date', show_date)
        item_bangumi.add_value('area_names', area_names)
        item_bangumi.add_value('language', language)
        item_bangumi.add_value('status', status)
        item_bangumi.add_value('introduction', introduction)
        item_bangumi.add_value('update_time', update_time)
        item_bangumi.add_value('table_name', 'animation_bangumi')
        yield item_bangumi.load_item()

        episodes = response.xpath('//div[@class="playlist pslpx"]').extract()[0]
        playee_names=Selector(text=episodes).xpath('//div[@class="playlist pslpx"]/p//span/text()').extract()
        episodess = Selector(text=episodes).xpath('//div[@class="playlist pslpx"]/ul').extract()
        episode_size=len(playee_names)
        for idx in range(0,episode_size):
            playee_name = playee_names[idx]
            episodes = Selector(text=episodess[idx]).xpath('//ul//li').extract()
            for episode in episodes:
                episode_name=Selector(text=episode).xpath('//li/a/@title').extract()[0]
                episode_url = 'https://www.jiadiandm.com'+Selector(text=episode).xpath('//li/a/@href').extract()[0]
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