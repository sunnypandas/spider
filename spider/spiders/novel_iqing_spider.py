# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, NovelNoberuItem, NovelChapterItem


class IQingSpider(scrapy.Spider):
    name = "iqing"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF,
        #'DOWNLOAD_DELAY': 3
    }
    allowed_domains = ['www.iqing.com']
    batch_date = datetime.datetime.now().date()
    default_data = {

    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {

    }
    def start_requests(self):
        for idx in range(1,100):
            yield scrapy.Request(
                url='https://poi.iqing.com/kensaku/?offset='+str((idx-1)*100)+'&limit=100&q=&fields=id%2Cindex_name%2Ctitle%2Curl%2Ccover%2Chumanize_count%2Cauthor_name%2Cintro%2Cbelief%2Ccombat%2Cfollow_count%2Cbf_count&type=book&order=0&p='+str(idx),
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        basic_info=response.text
        if 'results' in eval(basic_info.replace('null', 'None').replace('false', 'None').replace('true', 'None')):
            results=eval(basic_info.replace('null', 'None').replace('false', 'None').replace('true', 'None'))['results']
            for result in results:
                url='https://www.iqing.com'+result['url']
                img=result['cover']
                name = result['title']
                author_names=result['author_name']
                size=result['humanize_count']
                introduction=result['intro']
                yield scrapy.Request(
                    url=url, headers=self.default_headers, body=self.default_data, meta={'img':img,'name':name,'author_names':author_names,'size':size,'introduction':introduction}, callback=self.parse_detail_info, dont_filter=True)

    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name = response.meta['name']
        author_names = response.meta['author_names']
        size = response.meta['size']
        introduction = response.meta['introduction']
        status=''
        if len(response.xpath('//span[@class="book-tag tag-serial"]/text()').extract())>0:
            status=response.xpath('//span[@class="book-tag tag-serial"]/text()').extract()[0]
        if len(response.xpath('//span[@class="book-tag tag-end"]/text()').extract())>0:
            status=response.xpath('//span[@class="book-tag tag-end"]/text()').extract()[0]
        update_time = response.xpath('//span[@itemprop="datePublished"]/text()').extract()[0]
        type = response.xpath('//p[@id="cat-list"]').extract()[0]
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

        chapters=response.xpath('//div[@id="book-menu"]/ul[@itemprop="articleSection"]/li').extract()
        for chapter in chapters:
            part_name=Selector(text=chapter).xpath('//li/h3[@class="volume-title"]/text()').extract()[0]
            subchapters = Selector(text=chapter).xpath('//li/ul/li').extract()
            for subchapter in subchapters:
                chapter_name = part_name+Selector(text=subchapter).xpath('//li//a/@title').extract()[0]
                chapter_url = 'https://www.iqing.com'+Selector(text=subchapter).xpath('//li//a/@href').extract()[0]
                item_chapter = SpiderLoaderItem(item=NovelChapterItem(), response=response)
                item_chapter.add_value('batch_date', self.batch_date)
                item_chapter.add_value('noberu_url', url)
                item_chapter.add_value('chapter_name', chapter_name)
                item_chapter.add_value('chapter_url', chapter_url)
                item_chapter.add_value('table_name', 'novel_chapter')
                yield item_chapter.load_item()