# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, \
    MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, ComicMangaItem, ComicChapterItem


class Dmzj(scrapy.Spider):
    name = "dmzj"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
    }
    allowed_domains = ['www.dmzj.com']
    batch_date = datetime.datetime.now().date()
    default_data = {
    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'UM_distinctid=162eb46a35a0-0ae153d29407408-17347840-144000-162eb46a35c160; show_tip_1=0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
        'Referer': 'https://www.dmzj.com/',
        'Host': 'images.dmzj.com'
    }
    def start_requests(self):
        yield scrapy.Request(
            url='https://www.dmzj.com/category',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        total_page = response.xpath('//div[@class="bottom_page page"]//a[@class="pg_last"]/@href').extract()[0]
        start = '/category/0-0-0-0-0-0-'
        end = '.html'
        pages = int((total_page.split(start))[1].split(end)[0])
        for page in range(1,pages+1):
            #time.sleep(random.uniform(3, 5))
            yield scrapy.Request(
                url='https://www.dmzj.com/category/0-0-0-0-0-0-'+str(page)+'.html',
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="wrap_list_con autoHeight"]//div[@class="tab-con tab-content-selected autoHeight"]/ul[@class="list_con_li"]//li').extract()
        for content in contents:
            url = Selector(text=content).xpath('//li/a[@class="comic_img"]/@href').extract()[0]
            img = Selector(text=content).xpath('//li/a[@class="comic_img"]/img/@src').extract()[0]
            name = Selector(text=content).xpath('//li/span[@class="comic_list_det"]/h3/a/text()').extract()[0]
            author_names=Selector(text=content).xpath('//li/span[@class="comic_list_det"]//p[1]/text()').extract()[0][3:]
            type = Selector(text=content).xpath('//li/span[@class="comic_list_det"]//p[2]/text()').extract()[0][3:]
            status_part1 = Selector(text=content).xpath('//li/span[@class="comic_list_det"]//p[3]/text()').extract()[0][3:]
            status_part2 = Selector(text=content).xpath('//li/span[@class="comic_list_det"]//p[4]/text()').extract()[0][3:]
            status=status_part1+status_part2
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, meta={'img':img,'name':name,'author_names':author_names,'type':type,'status':status}, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name = response.meta['name']
        author_names = response.meta['author_names']
        type = response.meta['type']
        status = response.meta['status']
        introduction=None
        if len(response.xpath('//div[@class="comic_deCon"]//p[@class="comic_deCon_d"]').extract())>0:
            introduction = response.xpath('//div[@class="comic_deCon"]//p[@class="comic_deCon_d"]').extract()[0]
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
        item_manga.add_value('table_name', 'comic_manga')
        yield item_manga.load_item()

        allchapters=response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="zj_list autoHeight"]').extract()
        size=len(allchapters)
        for idx in range(0,size):
            subchapter= allchapters[idx]
            chapters=Selector(text=subchapter).xpath('//div[@class="zj_list autoHeight"]//div[@class="tab-content tab-content-selected zj_list_con autoHeight"]/ul//li').extract()
            parts_name=Selector(text=subchapter).xpath('//div[@class="zj_list autoHeight"]//div[@class="zj_list_head"]/h2/text()').extract()[0]
            for chapter in chapters:
                chapter_name=None
                if len(Selector(text=chapter).xpath('//li/a//span[@class="list_con_zj"]/text()').extract())>0:
                    chapter_name=(parts_name+Selector(text=chapter).xpath('//li/a//span[@class="list_con_zj"]/text()').extract()[0]).strip()
                chapter_url=None
                if len(Selector(text=chapter).xpath('//li/a/@href').extract())>0:
                    chapter_url = Selector(text=chapter).xpath('//li/a/@href').extract()[0]
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