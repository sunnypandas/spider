# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from flask import json
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, AnimationEpisodeItem, AnimationBangumiItem


class DaerdySpider(scrapy.Spider):
    name = "daerdy"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
    }
    allowed_domains = ['www.daerdy.com']
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
        'Connection': 'keep-alive',
        'Host': 'www.daerdy.com'
    }
    def start_requests(self):
        yield scrapy.Request(
            url='http://www.daerdy.com/vod-show-id-3-p-1.html',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)
    def get_final_url(self, response):
        urls = response.xpath('//div[@id="content"]//div[@class="ui-cnt"]//div[@class="ui-pages"]//a').extract()
        total_page = Selector(text=urls[2]).xpath('//a/@href').extract()[0]
        start = '/vod-show-id-3-p-'
        end = '.html'
        pages = int((total_page.split(start))[1].split(end)[0])
        for page in range(1,pages+1):
            #time.sleep(random.uniform(3, 5))
            yield scrapy.Request(
                url='http://www.daerdy.com/vod-show-id-3-p-'+str(page)+'.html',
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@id="content"]//div[@class="ui-cnt"]//ul[@class="primary-list min-video-list fn-clear"]//li').extract()
        for content in contents:
            url = 'http://www.daerdy.com'+Selector(text=content).xpath('//a[@class="play-pic"]/@href').extract()[0]
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        content = response.xpath('//div[@id="content"]//div[@id="detail-focus"]').extract()[0]
        introduction = response.xpath('//div[@id="detail-intro"]').extract()
        img = Selector(text=content).xpath('//div[@id="detail-focus"]//div[@class="detail-pic fn-left"]//img/@src').extract()[0]
        name = Selector(text=content).xpath('//div[@id="detail-focus"]//div[@class="detail-pic fn-left"]//img/@alt').extract()[0]
        actor_names = Selector(text=content).xpath('//div[@id="detail-focus"]//div[@class="detail-info"]//dl[1]//dd').extract()
        director_names = Selector(text=content).xpath('//div[@id="detail-focus"]//div[@class="detail-info"]//dl[2]//dd[1]').extract()
        show_date=Selector(text=content).xpath('//div[@id="detail-focus"]//div[@class="detail-info"]//dl[2]//dd[2]/text()').extract()[0]
        area_names = Selector(text=content).xpath('//div[@id="detail-focus"]//div[@class="detail-info"]//dl[3]//dd[1]/span/text()').extract()[0]
        language = Selector(text=content).xpath('//div[@id="detail-focus"]//div[@class="detail-info"]//dl[3]//dd[2]/span/text()').extract()[0]
        status = Selector(text=content).xpath('//div[@id="detail-focus"]//div[@class="detail-info"]//dl[4]//dd[1]/em/text()').extract()[0]
        update_time = Selector(text=content).xpath('//div[@id="detail-focus"]//div[@class="detail-info"]//dl[5]//dd[1]/span/text()').extract()[0]
        item = SpiderLoaderItem(item=AnimationBangumiItem(image_urls=[img]), response=response)
        item.add_value('batch_date', self.batch_date)
        item.add_value('host', self.allowed_domains[0])
        item.add_value('url', url)
        item.add_value('img', img)
        item.add_value('name', name)
        item.add_value('actor_names', actor_names)
        item.add_value('director_names', director_names)
        item.add_value('show_date', show_date)
        item.add_value('area_names', area_names)
        item.add_value('language', language)
        item.add_value('status', status)
        item.add_value('introduction', introduction)
        item.add_value('update_time', update_time)
        item.add_value('table_name', 'animation_bangumi')
        yield item.load_item()

        request_episode_url = url + '0-1.html'
        yield scrapy.Request(
            url=request_episode_url,
            headers=self.default_headers, body=self.default_data, meta={'bangumi_url': url},
            callback=self.parse_episode_info, dont_filter=True)

    def parse_episode_info(self, response):
        bangumi_url=response.meta['bangumi_url']
        contents = response.xpath('//div[@class="player"]//script/@src').extract()
        to_play_url = 'http://www.daerdy.com' + contents[0]
        play_js_src = 'http://www.daerdy.com' + contents[1]
        other_play_js_src = 'http://www.daerdy.com' + contents[2]
        yield scrapy.Request(
            url=to_play_url,headers=self.default_headers, body=self.default_data,
            meta={'bangumi_url': bangumi_url,'play_js_src': play_js_src,'other_play_js_src': other_play_js_src}, callback=self.parse_playee_info, dont_filter=True)

    def parse_playee_info(self, response):
        bangumi_url = response.meta['bangumi_url']
        contents = json.loads(response.text[13:-2])
        vod=contents['Vod']
        datas=contents['Data']
        for data in datas:
            playee_name = data['playname']
            playurls = data['playurls']
            for playurl in playurls:
                episode_name = playurl[0]
                playee_url = playurl[1]
                episode_url = 'http://www.daerdy.com' + playurl[2]
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