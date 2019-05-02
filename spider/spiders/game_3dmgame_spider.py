# -*- coding: utf-8 -*-
import datetime
import urllib
from math import ceil

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, GameGeimuItem, GameDownloadItem


class DmGame3(scrapy.Spider):
    name = "3dmgame"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF,
        # 'DOWNLOAD_DELAY': 3
    }
    allowed_domains = ['www.3dmgame.com']
    batch_date = datetime.datetime.now().date()
    default_data = {

    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {

    }
    def start_requests(self):
        yield scrapy.Request(
            url='http://dl.3dmgame.com/all/',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        total_page = response.xpath('//div[@class="info_bar"]//span/text()').extract()[0]
        pages = ceil(int(total_page)/15.0)
        for page in range(1,pages+1):
            url=''
            if page==1:
                url='http://dl.3dmgame.com/all'
            else:
                url='http://dl.3dmgame.com/all/'+str(page)+'/'
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="list_con"]//ul[@class="game_list"]//li').extract()
        for content in contents:
            img=Selector(text=content).xpath('//li//div[@class="img"]//a//img/@src').extract()[0]
            if img!='' and img!=None and img!=[] and not img.startswith('http'):
                img='http://dl.3dmgame.com'+img
            name = Selector(text=content).xpath('//li//div[@class="img"]//a//img/@alt').extract()[0]
            zh_name = Selector(text=content).xpath('//li//div[@class="img"]//a//img/@alt').extract()[0]
            url=Selector(text=content).xpath('//li//div[@class="img"]//a/@href').extract()[0]
            introduction=Selector(text=content).xpath('//li//div[@class="text"]/dl').extract()[0]
            type = Selector(text=content).xpath('//li//div[@class="more_info"]/dl//dd[1]/a/text()').extract()[0]
            update_time = Selector(text=content).xpath('//li//div[@class="more_info"]/dl//dd[2]/text()').extract()[0]
            size = Selector(text=content).xpath('//li//div[@class="more_info"]/dl//dd[3]/text()').extract()[0]
            language=''
            if len(Selector(text=content).xpath('//li//div[@class="more_info"]/dl//dd[4]/text()').extract())>0:
                language = Selector(text=content).xpath('//li//div[@class="more_info"]/dl//dd[4]/text()').extract()[0]
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, meta={'img':img,'name':name,'zh_name':zh_name,'introduction':introduction,'type':type,'update_time':update_time,'size':size,'language':language}, dont_filter=True)

    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name = response.meta['name']
        zh_name=response.meta['zh_name']
        introduction = response.meta['introduction']
        type = response.meta['type']
        update_time = response.meta['update_time']
        size = response.meta['size']
        language = response.meta['language']
        creator_name=''
        if len(response.xpath('//div[@class="game_info"]//ul//li[3]//div[@class="icontent"]/text()').extract())>0:
            creator_name = response.xpath('//div[@class="game_info"]//ul//li[3]//div[@class="icontent"]/text()').extract()[0]
        item_geimu = SpiderLoaderItem(item=GameGeimuItem(image_urls=[img]), response=response)
        item_geimu.add_value('batch_date', self.batch_date)
        item_geimu.add_value('host', self.allowed_domains[0])
        item_geimu.add_value('url', url)
        item_geimu.add_value('img', img)
        item_geimu.add_value('name', name)
        item_geimu.add_value('zh_name', zh_name)
        item_geimu.add_value('creator_name', creator_name)
        item_geimu.add_value('type', type)
        item_geimu.add_value('size', size)
        item_geimu.add_value('update_time', update_time)
        item_geimu.add_value('language', language)
        item_geimu.add_value('introduction', introduction)
        item_geimu.add_value('category', '游戏')
        item_geimu.add_value('table_name', 'game_geimu')
        yield item_geimu.load_item()

        is_fake_downloads=False
        if len(response.xpath('//div[@class="down_add"]//div[@class="dowlnew"]//div[@class="wp-dowl"]/ul[@class="nxzdownload"]').extract())>0:
            is_fake_downloads = True
        if is_fake_downloads==False:
            downloads=[]
            if len(response.xpath('//div[@class="down_add"]//div[@class="dowlnew"]//div[@class="wp-dowl"]//div[@class="wpdowl-right"]/p/a/@href').extract())>0:
                download01_url = response.xpath('//div[@class="down_add"]//div[@class="dowlnew"]//div[@class="wp-dowl"]//div[@class="wpdowl-right"]/p/a/@href').extract()[0]
                download01_name = response.xpath('//div[@class="down_add"]//div[@class="dowlnew"]//div[@class="wp-dowl"]//div[@class="wpdowl-right"]/p/a/text()').extract()[0]
                downloads.append({'download_name':download01_name,'download_url':download01_url})
            if len(response.xpath('//div[@class="down_add"]//div[@class="dowlnew"]//div[@class="wp-dowl"]//div[@class="dmmdowl"]//div[@class="wpdowl-right"]/ul//li').extract()) > 0:
                download02s=response.xpath('//div[@class="down_add"]//div[@class="dowlnew"]//div[@class="wp-dowl"]//div[@class="dmmdowl"]//div[@class="wpdowl-right"]/ul//li').extract()
                for download02 in download02s:
                    download02_url=Selector(text=download02).xpath('//li/a/@href').extract()[0]
                    download02_name = Selector(text=download02).xpath('//li/a/text()').extract()[0]
                    downloads.append({'download_name': download02_name, 'download_url': download02_url})
            for download in downloads:
                download_name = download['download_name']
                download_url = download['download_url']
                item_download = SpiderLoaderItem(item=GameDownloadItem(), response=response)
                item_download.add_value('batch_date', self.batch_date)
                item_download.add_value('game_url', url)
                item_download.add_value('download_name', download_name)
                item_download.add_value('download_url', download_url)
                item_download.add_value('table_name', 'game_download')
                yield item_download.load_item()
        else:
            fake_download_url='http://box.hyds360.com/down/'+str(url[url.rfind('/')+1:-5])+'-2.html'
            yield scrapy.Request(
                url=fake_download_url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_download_info, meta={'game_url':url}, dont_filter=True)
    def parse_download_info(self, response):
        downloads=[]
        if len(response.xpath('//a[@class="gameDown down_xl"]/@href').extract())>0:
            download01_url = response.xpath('//a[@class="gameDown down_xl"]/@href').extract()[0]
            downloads.append({'download_name': '迅雷链接下载', 'download_url': download01_url})
        if len(response.xpath('//a[@class="gameDown down_bd"]/@href').extract())>0:
            download02_url = response.xpath('//a[@class="gameDown down_bd"]/@href').extract()[0]
            downloads.append({'download_name': '网盘下载', 'download_url': download02_url})
        for download in downloads:
            download_name = download['download_name']
            download_url = download['download_url']
            item_download = SpiderLoaderItem(item=GameDownloadItem(), response=response)
            item_download.add_value('batch_date', self.batch_date)
            item_download.add_value('game_url', response.meta['game_url'])
            item_download.add_value('download_name', download_name)
            item_download.add_value('download_url', download_url)
            item_download.add_value('table_name', 'game_download')
            yield item_download.load_item()