# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy import Selector

from spider.consts import MYSQL_ITEM_PIPELINES, \
    DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
from spider.items import SpiderLoaderItem, ComicMangaItem, ComicChapterItem


class MH177Spider(scrapy.Spider):
    name = "177mh"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
    }
    allowed_domains = ['www.177mh.com']
    batch_date = datetime.datetime.now().date()
    default_data = {
    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
        # 'Accept': 'text/html, application/xhtml+xml, */*',
        # 'Accept-Encoding': 'gzip, deflate',
        # 'Accept-Language': 'zh-CN',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        # 'DNT': '1',
        # 'Connection': 'Keep-Alive',
        # 'Host': 'www.177mh.com'
    }
    def start_requests(self):
        yield scrapy.Request(
            url='https://www.177mh.com/wanjie/index_10.html',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, meta={'type': 'wanjie'},dont_filter=True)
        yield scrapy.Request(
            url='https://www.177mh.com/lianzai/index_10.html',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, meta={'type': 'lianzai'},dont_filter=True)
    def get_final_url(self, response):
        total_page = response.xpath('//div[@id="main"]//div[@class="main_left"]//div[@class="ar_list"]//div[@class="pages_s"]/span/text()').extract()[1][1:]
        pages = int(total_page)
        for page in range(0,pages):
            #time.sleep(random.uniform(3, 5))
            url=None
            if page==0:
                url='https://www.177mh.com/'+response.meta['type']+'/index.html'
            else:
                url = 'https://www.177mh.com/'+response.meta['type']+'/index_'+str(page)+'.html'
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        urls=None
        if len(response.xpath('//div[@id="main"]//div[@class="main_left"]//div[@class="ar_list"]//div[@class="ar_list_co"]/ul').extract())>0:
            urls=response.xpath('//div[@id="main"]//div[@class="main_left"]//div[@class="ar_list"]//div[@class="ar_list_co"]/ul//li/a/@href').extract()
        else:
            urls = response.xpath('//div[@id="main"]//div[@class="main_left"]//div[@class="ar_list"]//div[@class="ar_list_co"]//dl/dt/a/@href').extract()
        for url in urls:
            yield scrapy.Request(
                url='https://www.177mh.com'+url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        content = response.xpath('//div[@id="main"]//div[@class="main_left"]//div[@class="ar_list"]//div[@class="ar_list_coc"]/dl').extract()[0]
        img=Selector(text=content).xpath('//dl/dt/img/@src').extract()[0]
        name = Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[1]/h1/text()').extract()[0]
        type=None
        if len(response.xpath('//div[@id="main"]//div[@class="main_left"]//div[@class="ar_list"]/h3/a/text()').extract())>0:
            type=response.xpath('//div[@id="main"]//div[@class="main_left"]//div[@class="ar_list"]/h3/a/text()').extract()[0]
        author_names=None
        if len(Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[2]//a/text()').extract())>0:
            author_names = Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[2]//a/text()').extract()[0]
        status_part1=''
        status_part2 = ''
        if len(Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[3]//a/text()').extract())>0:
            status_part1=Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[3]//a/text()').extract()[0]
        if len(Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[4]/text()').extract())>0:
            status_part2=Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[4]/text()').extract()[0]
        status = status_part1+status_part2
        update_time=None
        if len(Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[5]/text()').extract())>0:
            update_time = Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[5]/text()').extract()[0]
        introduction = Selector(text=content).xpath('//dl/dd/ul[@class="ar_list_coc"]//li[6]/p').extract()[0]
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
        item_manga.add_value('update_time', update_time)
        item_manga.add_value('table_name', 'comic_manga')
        yield item_manga.load_item()

        chapters=response.xpath('//div[@id="main"]//div[@class="main_left"]//div[@class="ar_list"]//div[@class="ar_list_coc"]//ul[@class="ar_rlos_bor ar_list_col"]//li').extract()
        for chapter in chapters:
            chapter_name=None
            if len(Selector(text=chapter).xpath('//li/a/text()').extract())>0:
                chapter_name=Selector(text=chapter).xpath('//li/a/text()').extract()[0]
            chapter_url=None
            if len(Selector(text=chapter).xpath('//li/a/@href').extract())>0:
                chapter_url = 'https://www.177mh.com'+Selector(text=chapter).xpath('//li/a/@href').extract()[0]
            item_chapter = SpiderLoaderItem(item=ComicChapterItem(), response=response)
            item_chapter.add_value('batch_date', self.batch_date)
            item_chapter.add_value('manga_url', url)
            item_chapter.add_value('chapter_name', chapter_name)
            item_chapter.add_value('chapter_url', chapter_url)
            item_chapter.add_value('table_name', 'comic_chapter')
            yield item_chapter.load_item()