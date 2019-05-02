# -*- coding: utf-8 -*-
import datetime
import urllib
from math import ceil

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, GameGeimuItem, GameDownloadItem


class GamerSkySpider(scrapy.Spider):
    name = "gamersky"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF,
        # 'DOWNLOAD_DELAY': 3
    }
    allowed_domains = ['www.gamersky.com']
    batch_date = datetime.datetime.now().date()
    default_data = {

    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
        'Cache-Control': 'max-age=0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5,zh-TW;q=0.4',
        'Cookie': 'UM_distinctid=163267162a3347-023bcd26015c29-f373567-1fa400-163267162a449a; Hm_lvt_dcb5060fba0123ff56d253331f28db6a=1525358336,1525529117; CNZZDATA5448511=cnzz_eid%3D1406676255-1525357290-null%26ntime%3D1525526927; Hm_lvt_2fcf511ac55c97a76f86b396e941b641=1525358357,1525529138; Hm_lpvt_2fcf511ac55c97a76f86b396e941b641=1525529574; Hm_lpvt_dcb5060fba0123ff56d253331f28db6a=1525531914',
        'Upgrade-Insecure-Requests': 1,
        'Referer': 'http://down.gamersky.com/pc/?sort=30&list=1',
        'Connection': 'keep-alive',
        'Host': 'down.gamersky.com'
    }
    def start_requests(self):
        yield scrapy.Request(
            url='http://down.gamersky.com/pc/',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        total_page = response.xpath('//div[@class="Mid"]//div[@class="Mid2"]//div[@class="dtop_R"]//span[@class="num"]/text()').extract()[0]
        pages = ceil(int(total_page)/20.0)
        for page in range(1,pages+1):
            yield scrapy.Request(
                url='http://down.gamersky.com/page/pc/0-0-0-0-0-0-0-00_'+str(page)+'.html',
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//ul[@class="down_con downData"]//li').extract()
        for content in contents:
            img=Selector(text=content).xpath('//li//div[@class="img"]/a/img/@src').extract()[0]
            if img!='' and img!=None and img!=[] and not img.startswith('http'):
                img='http://img4.gamersky.com/Files/GamerSky/'+img
            name = Selector(text=content).xpath('//li//div[@class="img"]/a/@title').extract()[0]
            url=Selector(text=content).xpath('//li//div[@class="img"]/a/@href').extract()[0]
            update_time = Selector(text=content).xpath('//li//div[@class="txt"][1]/text()').extract()[0]
            if update_time!=None:
                update_time=update_time.split('：')[1]
            type = Selector(text=content).xpath('//li//div[@class="txt"][2]/text()').extract()[0]
            if type!=None:
                type=type.split('：')[1]
            language = Selector(text=content).xpath('//li//div[@class="txt"][3]/text()').extract()[0]
            if language!=None:
                language=language.split('：')[1]
            size = Selector(text=content).xpath('//li//div[@class="txt"][4]/text()').extract()[0]
            if size!=None:
                size=size.split('：')[1]
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, meta={'img':img,'name':name,'update_time':update_time,'type':type,'language':language,'size':size}, dont_filter=True)

    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name = response.meta['name']
        update_time = response.meta['update_time']
        type = response.meta['type']
        language = response.meta['language']
        size = response.meta['size']
        zh_name=''
        if len(response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][1]//li[1]//div[@class="txt"]/text()').extract())>0:
            zh_name=response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][1]//li[1]//div[@class="txt"]/text()').extract()[0].strip()
        publish_date=''
        if len(response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][1]//li[2]//div[@class="txt"]/text()').extract())>0:
            publish_date = response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][1]//li[2]//div[@class="txt"]/text()').extract()[0].strip()
        en_name=''
        if len(response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][2]//li[1]//div[@class="txt"]/text()').extract())>0:
            en_name = response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][2]//li[1]//div[@class="txt"]/text()').extract()[0].strip()
        creator_name=''
        if len(response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][2]//li[2]//div[@class="txt"]/text()').extract())>0:
            creator_name = response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][2]//li[2]//div[@class="txt"]/text()').extract()[0].strip()
        publisher_name=''
        if len(response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][2]//li[3]//div[@class="txt"]/text()').extract())>0:
            publisher_name = response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][2]//li[3]//div[@class="txt"]/text()').extract()[0].strip()
        show_date=''
        if len(response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][2]//li[4]//div[@class="txt"]/text()').extract())>0:
            show_date = response.xpath('//div[@class="game"]//div[@class="con"]//div[@class="info"]//ul[@class="YXXX"][2]//li[4]//div[@class="txt"]/text()').extract()[0].strip()
        introduction=''
        if len(response.xpath('//div[@class="Mid2L_con"]//div[@class="intr"]').extract())>0:
            introduction=response.xpath('//div[@class="Mid2L_con"]//div[@class="intr"]').extract()[0]
        item_geimu = SpiderLoaderItem(item=GameGeimuItem(image_urls=[img]), response=response)
        item_geimu.add_value('batch_date', self.batch_date)
        item_geimu.add_value('host', self.allowed_domains[0])
        item_geimu.add_value('url', url)
        item_geimu.add_value('img', img)
        item_geimu.add_value('name', name)
        item_geimu.add_value('zh_name', zh_name)
        item_geimu.add_value('en_name', en_name)
        item_geimu.add_value('creator_name', creator_name)
        item_geimu.add_value('publisher_name', publisher_name)
        item_geimu.add_value('language', language)
        item_geimu.add_value('type', type)
        item_geimu.add_value('update_time', update_time)
        item_geimu.add_value('publish_date', publish_date)
        item_geimu.add_value('show_date', show_date)
        item_geimu.add_value('size', size)
        item_geimu.add_value('category', '游戏')
        item_geimu.add_value('introduction', introduction)
        item_geimu.add_value('table_name', 'game_geimu')
        yield item_geimu.load_item()

        downloads=response.xpath('//div[@class="Download"]/div[@class="dl_url"]//a').extract()
        for download in downloads:
            download_name = Selector(text=download).xpath('//a/text()').extract()[0]
            download_url = Selector(text=download).xpath('//a/@href').extract()[0]
            item_download = SpiderLoaderItem(item=GameDownloadItem(), response=response)
            item_download.add_value('batch_date', self.batch_date)
            item_download.add_value('game_url', url)
            item_download.add_value('download_name', download_name)
            item_download.add_value('download_url', download_url)
            item_download.add_value('table_name', 'game_download')
            yield item_download.load_item()