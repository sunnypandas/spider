# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy.spiders.init import InitSpider
from scrapy import Selector
from scrapy_splash import SplashRequest
from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, NovelNoberuItem, NovelChapterItem


class SFAcgSpider(scrapy.Spider):
    name = "sfacg"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF,
        #'DOWNLOAD_DELAY': 3
    }
    allowed_domains = ['www.sfacg.com']
    batch_date = datetime.datetime.now().date()
    default_data = {
    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
    }

    def start_requests(self):
        yield scrapy.Request(
            url='http://book.sfacg.com/List/?tid=-1', headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        total_page = response.xpath('//ul[@class="nav pagebar"]/li[4]/a/text()').extract()[0]
        pages = int(total_page)
        for page in range(1,pages+1):
            yield scrapy.Request(
                url='http://book.sfacg.com/List/default.aspx?tid=-1&PageIndex='+str(page),
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="comic_cover Blue_link3"]/ul[@class="Comic_Pic_List"]').extract()
        for content in contents:
            img = Selector(text=content).xpath('//ul[@class="Comic_Pic_List"]/li[@class="Conjunction"]/a/img/@src').extract()[0]
            url='http://book.sfacg.com'+Selector(text=content).xpath('//ul[@class="Comic_Pic_List"]/li[@class="Conjunction"]/a/@href').extract()[0]
            name = Selector(text=content).xpath('//ul[@class="Comic_Pic_List"]/li[@class="Conjunction"]/a/img/@alt').extract()[0]
            yield scrapy.Request(url=url, meta={'img':img,'name':name}, callback=self.parse_detail_info, dont_filter=True)

    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name = response.meta['name']
        spans=response.xpath('//div[@class="count-detail"]//span').extract()
        author_names=response.xpath('//div[@class="author-name"]/span/text()').extract()[0]
        size=Selector(text=spans[1]).xpath('//span/text()').extract()[0].split('：')[1].split('[')[0]
        status_part1=Selector(text=spans[1]).xpath('//span/text()').extract()[0].split('：')[1].split('[')[1][0:-1]
        status_part2=''
        if len(response.xpath('//div[@class="chapter-info"]//h3[@class="chapter-title"]/a[@class="link"]/text()').extract())>0:
            status_part2 =  response.xpath('//div[@class="chapter-info"]//h3[@class="chapter-title"]/a[@class="link"]/text()').extract()[0]
        status=status_part1+status_part2
        introduction = response.xpath('//p[@class="introduce"]').extract()[0]
        update_time=Selector(text=spans[3]).xpath('//span/text()').extract()[0][3:]
        type=Selector(text=spans[0]).xpath('//span/text()').extract()[0].split('：')[1]
        item_noberu = SpiderLoaderItem(item=NovelNoberuItem(image_urls=[img]), response=response)
        item_noberu.add_value('batch_date', self.batch_date)
        item_noberu.add_value('host', self.allowed_domains[0])
        item_noberu.add_value('url', url)
        item_noberu.add_value('img', img)
        item_noberu.add_value('name', name)
        item_noberu.add_value('author_names', author_names)
        item_noberu.add_value('status', status)
        item_noberu.add_value('type', type)
        item_noberu.add_value('size', size)
        item_noberu.add_value('category', '轻小说')
        item_noberu.add_value('introduction', introduction)
        item_noberu.add_value('update_time', update_time)
        item_noberu.add_value('table_name', 'novel_noberu')
        yield item_noberu.load_item()

        tmp_url = ''
        if len(response.xpath('//div[@id="BasicOperation"]/a[1]/@href').extract()) > 0:
            tmp_url = 'http://book.sfacg.com'+response.xpath('//div[@id="BasicOperation"]/a[1]/@href').extract()[0]
            if tmp_url.find('javascript')<=0:
                yield scrapy.Request(url=tmp_url, meta={'noberu_url': url}, callback=self.parse_chapter_info, dont_filter=True)

    def parse_chapter_info(self, response):
        noberu_url=response.meta['noberu_url']
        chapters=response.xpath('//div[@class="story-catalog"]').extract()
        for chapter in chapters:
            part_name=Selector(text=chapter).xpath('//div[@class="story-catalog"]/div[@class="catalog-hd"]/h3[@class="catalog-title"]/text()').extract()[0]
            subchapters=Selector(text=chapter).xpath('//div[@class="story-catalog"]/div[@class="catalog-list"]/ul/li').extract()
            for subchapter in subchapters:
                if len(Selector(text=subchapter).xpath('//li/a/@title').extract())>0:
                    chapter_name = part_name+Selector(text=subchapter).xpath('//li/a/@title').extract()[0]
                chapter_url = ''
                if len(Selector(text=subchapter).xpath('//li/a/@href').extract())>0:
                    chapter_url = 'http://book.sfacg.com'+Selector(text=subchapter).xpath('//li/a/@href').extract()[0]
                item_chapter = SpiderLoaderItem(item=NovelChapterItem(), response=response)
                item_chapter.add_value('batch_date', self.batch_date)
                item_chapter.add_value('noberu_url', noberu_url)
                item_chapter.add_value('chapter_name', chapter_name)
                item_chapter.add_value('chapter_url', chapter_url)
                item_chapter.add_value('table_name', 'novel_chapter')
                yield item_chapter.load_item()