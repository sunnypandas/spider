# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_ON, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, ComicMangaItem, ComicChapterItem


class Manhuagui(scrapy.Spider):
    name = "manhuagui"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_ON,
        # 'DOWNLOAD_DELAY': 10
    }
    allowed_domains = ['www.manhuagui.com']
    batch_date = datetime.datetime.now().date()
    default_data = {
    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
    }
    def start_requests(self):
        yield scrapy.Request(
            url='http://www.manhuagui.com/list/',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        total_page = response.xpath('//div[@class="book-list"]//div[@class="pager-cont"]//div[@class="pager"]//a[last()]/@href').extract()[0]
        start = '/list/index_p'
        end = '.html'
        pages = int((total_page.split(start))[1].split(end)[0])
        for page in range(1,pages+1):
            #time.sleep(random.uniform(3, 5))
            yield scrapy.Request(
                url='http://www.manhuagui.com/list/index_p'+str(page)+'.html',
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="book-list"]//ul[@id="contList"]//li').extract()
        for content in contents:
            url = 'http://www.manhuagui.com'+Selector(text=content).xpath('//li/a[@class="bcover"]/@href').extract()[0]
            name=Selector(text=content).xpath('//li/a[@class="bcover"]/@title').extract()[0]
            img=None
            if len(Selector(text=content).xpath('//li/a[@class="bcover"]/img/@src').extract())>0:
                img = Selector(text=content).xpath('//li/a[@class="bcover"]/img/@src').extract()[0]
            else:
                img = Selector(text=content).xpath('//li/a[@class="bcover"]/img/@data-src').extract()[0]
            status_part2 = Selector(text=content).xpath('//li/a[@class="bcover"]//span[@class="tt"]/text()').extract()[0]
            update_time=Selector(text=content).xpath('//li//span[@class="updateon"]/text()').extract()[0][4:]
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, meta={'name':name,'img':img,'status_part2':status_part2,'update_time':update_time}, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name=response.meta['name']
        update_time = response.meta['update_time']
        status_part2 = response.meta['status_part2']
        status_part1=''
        if len(response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//ul[@class="detail-list cf"]//li[4]/span//span[1]/text()').extract()):
            status_part1 = response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//ul[@class="detail-list cf"]//li[4]/span//span[1]/text()').extract()[0]
        status=status_part1+status_part2
        type = response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//ul[@class="detail-list cf"]//li[2]//span[1]').extract()[0]
        author_names=response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//ul[@class="detail-list cf"]//li[2]//span[2]').extract()[0]
        show_date=None
        if len(response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//ul[@class="detail-list cf"]//li[1]//span[1]//a/text()').extract())>0:
            show_date =response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//ul[@class="detail-list cf"]//li[1]//span[1]//a/text()').extract()[0]
        area_names = None
        if len(response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//ul[@class="detail-list cf"]//li[1]//span[2]//a/text()').extract())>0:
            area_names = response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//ul[@class="detail-list cf"]//li[1]//span[2]//a/text()').extract()[0]
        introduction=None
        if len(response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//div[@class="book-intro"]//div[@id="intro-all"]').extract())>0:
            introduction = response.xpath('//div[@class="book-cont cf"]//div[@class="book-detail pr fr"]//div[@class="book-intro"]//div[@id="intro-all"]').extract()[0]
        item_manga = SpiderLoaderItem(item=ComicMangaItem(image_urls=[img]), response=response)
        item_manga.add_value('batch_date', self.batch_date)
        item_manga.add_value('host', self.allowed_domains[0])
        item_manga.add_value('url', url)
        item_manga.add_value('img', img)
        item_manga.add_value('name', name)
        item_manga.add_value('author_names', author_names)
        item_manga.add_value('status', status)
        item_manga.add_value('type', type)
        item_manga.add_value('introduction', introduction)
        item_manga.add_value('area_names', area_names)
        item_manga.add_value('show_date', show_date)
        item_manga.add_value('update_time', update_time)
        item_manga.add_value('table_name', 'comic_manga')
        yield item_manga.load_item()

        lenght=response.xpath('//div[@class="chapter cf mt16"]//h4/span/text()').extract()
        part_names = response.xpath('//div[@class="chapter cf mt16"]//h4/span/text()').extract()
        part_contents = response.xpath('//div[@class="chapter cf mt16"]//div[@class="chapter-list cf mt10"]').extract()
        size=len(lenght)
        for idx in range(1,size,2):
            chapters=Selector(text=part_contents[idx]).xpath('//div[@class="chapter-list cf mt10"]/ul//li').extract()
            parts_name=part_names[idx-1]
            for chapter in chapters:
                chapter_name=None
                if len(Selector(text=chapter).xpath('//li/a/@title').extract())>0:
                    chapter_name=(parts_name+Selector(text=chapter).xpath('//li/a/@title').extract()[0]).strip()
                chapter_url=None
                if len(Selector(text=chapter).xpath('//li/a/@href').extract())>0:
                    chapter_url = 'http://www.manhuagui.com'+Selector(text=chapter).xpath('//li/a/@href').extract()[0]
                item_chapter = SpiderLoaderItem(item=ComicChapterItem(), response=response)
                item_chapter.add_value('batch_date', self.batch_date)
                item_chapter.add_value('manga_url', url)
                item_chapter.add_value('chapter_name', chapter_name)
                item_chapter.add_value('chapter_url', chapter_url)
                item_chapter.add_value('table_name', 'comic_chapter')
                yield item_chapter.load_item()

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