# -*- coding: utf-8 -*-
import datetime
import urllib
from math import ceil

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_SQUID_PROXY_ON, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, GameGeimuItem, GameDownloadItem


class Ali213Spider(scrapy.Spider):
    name = "ali213"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_SQUID_PROXY_ON,
        # 'DOWNLOAD_DELAY': 1
    }
    allowed_domains = ['www.ali213.net']
    batch_date = datetime.datetime.now().date()
    default_data = {

    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
        'Cache-Control': 'max-age=0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5,zh-TW;q=0.4',
        'Cookie': 'UM_distinctid=163266add7e506-0cc0c8ebeaf0d5-f373567-1fa400-163266add7f8; bdshare_firstime=1525357966484; Hm_lvt_ef39e4f1e1037647abfbd15efdf8044f=1525357928,1525529010; Hm_lvt_90d3f2ca77e99acb3fad6f24d83a031d=1525590241; Hm_lpvt_90d3f2ca77e99acb3fad6f24d83a031d=1525590249; CNZZDATA680195=cnzz_eid%3D1598056172-1525353225-%26ntime%3D1525591806; Hm_lvt_2207c39aecfe7b9b0f144ab7f8316fad=1525357928,1525529010,1525592705; checkIMGCode=9185; CNZZDATA2573307=cnzz_eid%3D1431571239-1525353695-%26ntime%3D1525592465; Hm_lpvt_2207c39aecfe7b9b0f144ab7f8316fad=1525596098; Hm_lpvt_ef39e4f1e1037647abfbd15efdf8044f=1525596098',
        'Referer': 'http://down.ali213.net/new/index_2.html',
        'Upgrade-Insecure-Requests': 1,
        'Connection': 'keep-alive',
        'Host': 'down.ali213.net'
    }
    def start_requests(self):
        yield scrapy.Request(
            url='http://down.ali213.net/new/',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        total_page = response.xpath('//div[@class="list_body_page"]//a[1]//span[@class="sec"]/text()').extract()[0].split("/")[1]
        pages = int(total_page)
        # pages=10
        for page in range(1,pages+1):
            url=''
            if page==1:
                url='http://down.ali213.net/new/index.html'
            else:
                url='http://down.ali213.net/new/index_'+str(page)+'.html'
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="list_body"]//div[@class="list_body_contain"]//div[@class="list_body_con"]').extract()
        for content in contents:
            img=Selector(text=content).xpath('//div[@class="list_body_con"]//a[@class="list_body_con_img"]//img/@data-original').extract()[0]
            name = Selector(text=content).xpath('//div[@class="list_body_con"]//a[@class="list_body_con_img"]//img/@alt').extract()[0]
            zh_name = Selector(text=content).xpath('//div[@class="list_body_con"]//div[@class="list_body_con_con"]/a/text()').extract()[0]
            url_tmp=Selector(text=content).xpath('//div[@class="list_body_con"]//a[@class="list_body_con_img"]/@href').extract()[0]
            if not url_tmp.startswith('/'):
                continue
            url='http://down.ali213.net'+url_tmp
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, meta={'img':img,'name':name,'zh_name':zh_name}, dont_filter=True)

    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name = response.meta['name']
        zh_name=response.meta['zh_name']
        en_name=''
        if len(response.xpath('//div[@class="detail_body_down"]//div[@itemprop="alias"]/text()').extract())>0:
            en_name = response.xpath('//div[@class="detail_body_down"]//div[@itemprop="alias"]/text()').extract()[0]
        type=''
        if len(response.xpath('//div[@class="detail_body_down"]//div[@class="newdown_l_con_con_info"][1]/a/text()').extract())>0:
            type = response.xpath('//div[@class="detail_body_down"]//div[@class="newdown_l_con_con_info"][1]/a/text()').extract()[0]
        creator_name=''
        if len(response.xpath('//div[@class="detail_body_down"]//div[@class="newdown_l_con_con_info"][2]/text()').extract())>0:
            creator_name = response.xpath('//div[@class="detail_body_down"]//div[@class="newdown_l_con_con_info"][2]/text()').extract()[0].split('：')[1]
        publish_date = ''
        if len(response.xpath('//div[@class="detail_body_down"]//div[@class="newdown_l_con_con_info"][3]//span[@itemprop="dateModified"]/text()').extract())>0:
            publish_date = response.xpath('//div[@class="detail_body_down"]//div[@class="newdown_l_con_con_info"][3]//span[@itemprop="dateModified"]/text()').extract()[0]
        size=''
        if len(response.xpath('//div[@class="detail_body_down"]//div[@class="newdown_l_con_con_info"][4]//span[@itemprop="fileSize"]/text()').extract())>0:
            size = response.xpath('//div[@class="detail_body_down"]//div[@class="newdown_l_con_con_info"][4]//span[@itemprop="fileSize"]/text()').extract()[0]
        introduction=''
        if len(response.xpath('//div[@class="detail_body_con_bb"]//div[@class="detail_body_con_bb_con"]').extract())>0:
            introduction=response.xpath('//div[@class="detail_body_con_bb"]//div[@class="detail_body_con_bb_con"]').extract()[0]
        item_geimu = SpiderLoaderItem(item=GameGeimuItem(image_urls=[img]), response=response)
        item_geimu.add_value('batch_date', self.batch_date)
        item_geimu.add_value('host', self.allowed_domains[0])
        item_geimu.add_value('url', url)
        item_geimu.add_value('img', img)
        item_geimu.add_value('name', name)
        item_geimu.add_value('zh_name', zh_name)
        item_geimu.add_value('en_name', en_name)
        item_geimu.add_value('creator_name', creator_name)
        item_geimu.add_value('type', type)
        item_geimu.add_value('publish_date', publish_date)
        item_geimu.add_value('size', size)
        item_geimu.add_value('introduction', introduction)
        item_geimu.add_value('category', '游戏')
        item_geimu.add_value('table_name', 'game_geimu')
        yield item_geimu.load_item()

        if len(response.xpath('//div[@class="detail_down_adress_con"]/div[@class="detail_down_adress_con_bottom"]//div[@class="detail_down_adress_con_bottom_left"]//script[2]/text()').extract())>0:
            fake_down_url='http://www.soft50.com'+response.xpath('//div[@class="detail_down_adress_con"]/div[@class="detail_down_adress_con_bottom"]//div[@class="detail_down_adress_con_bottom_left"]//script[2]/text()').extract()[0][14:-2]
            yield scrapy.Request(
                url=fake_down_url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_fake_download_info,
                meta={'game_url': url}, dont_filter=True)

    def parse_fake_download_info(self, response):
        if len(response.xpath('//div[@class="result1"]//a/@href'))>0:
            fake_down_url=response.xpath('//div[@class="result1"]//a/@href').extract()[0]
            yield scrapy.Request(
                url=fake_down_url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_download_info,
                meta={'game_url': response.meta['game_url']}, dont_filter=True)

    def parse_download_info(self, response):
        downloads = []
        download01=''
        if len(response.xpath('//a[@id="jsbtn"]/@data-id').extract())>0:
            download01 = 'http://d.soft5566.com/setup_a'+str(response.xpath('//a[@id="jsbtn"]/@data-id').extract()[0])+'.exe'
            downloads.append({'download_name':'极速下载','download_url':download01})
        download02_url = response.xpath('//div[@class="n1_content"]//font/a/@href').extract()
        download02_name = response.xpath('//div[@class="n1_content"]//font/a/text()').extract()
        for idx in range(0,len(download02_url)):
            downloads.append({'download_name': download02_name[idx], 'download_url': download02_url[idx]})
        download03=''
        if len(response.xpath('//div[@class="ed2k_content"]//ul[@class="content_part"]//span/a/@href').extract())>0:
            download03 = response.xpath('//div[@class="ed2k_content"]//ul[@class="content_part"]//span/a/@href').extract()[0]
            downloads.append({'download_name':'eD2K下载地址','download_url':download03})
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