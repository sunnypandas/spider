# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, ComicMangaItem, ComicChapterItem


class MH930(scrapy.Spider):
    name = "930mh"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF,
        'DOWNLOAD_DELAY' : 3
    }
    allowed_domains = ['www.930mh.com']
    batch_date = datetime.datetime.now().date()
    default_data = {
    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
    }
    def start_requests(self):
        yield scrapy.Request(
            url='http://www.930mh.com/list/',
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        total_page = response.xpath('//ul[@class="pagination"][1]//li[@class="last"]/a/@href').extract()[0][6:-1]
        pages = int(total_page)
        urls=[]
        for page in range(1,pages+1):
        # for url in urls:
            #time.sleep(random.uniform(3, 5))
            yield scrapy.Request(
                url='http://www.930mh.com/list_'+str(page)+'/',
                # url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="wrap_list_con autoHeight"]//div[@class="tab-con tab-content-selected autoHeight"]/div[@class="list-view"]/ul[@class="list_con_li clearfix"]//li').extract()
        for content in contents:
            url = Selector(text=content).xpath('//li/a[@class="comic_img"]/@href').extract()[0]
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.parse_detail_info, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        img=None
        if len(response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_i"]//div[@class="comic_i_img"]/img/@src').extract())>0:
            img=response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_i"]//div[@class="comic_i_img"]/img/@src').extract()[0]
        name=None
        if len(response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]/h1[1]/text()').extract())>0:
            name = response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]/h1[1]/text()').extract()[0]
        update_time = None
        if len(response.xpath(
                '//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][2]/li[3]/text()').extract()):
            update_time = response.xpath(
                '//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][2]/li[3]/text()').extract()[0][3:].strip()
        status_part1=''
        if len(response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][1]/li[2]/a/text()').extract()):
            status_part1 = response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][1]/li[2]/a/text()').extract()[0]
        status_part2 = ''
        if len(response.xpath(
                '//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][2]/li[4]/a/text()').extract()):
            status_part2 = response.xpath(
                '//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][2]/li[4]/a/text()').extract()[0]
        status=status_part1+status_part2
        type = None
        if len(response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][1]/li[3]/a/text()').extract()):
            type = response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][1]/li[3]/a/text()').extract()[0]
        author_names=None
        if len(response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][1]/li[1]/a/text()').extract()):
            author_names = response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][1]/li[1]/a/text()').extract()[0]
        area_names = None
        if len(response.xpath(
                '//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][2]/li[1]/a/text()').extract()):
            area_names = response.xpath(
                '//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//div[@class="comic_deCon autoHeight"]//ul[@class="comic_deCon_liT"][2]/li[1]/a/text()').extract()[0]
        introduction=None
        if len(response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//p[@class="comic_deCon_d"]').extract())>0:
            introduction = response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="wrap_intro_l_comic autoHeight"]//p[@class="comic_deCon_d"]').extract()[0]
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
        item_manga.add_value('update_time', update_time)
        item_manga.add_value('table_name', 'comic_manga')
        yield item_manga.load_item()

        allchapters=response.xpath('//div[@class="wrap_intro_l widthEigLeft con_left"]//div[@class="zj_list autoHeight"]').extract()
        size=len(allchapters)
        for idx in range(1,size,2):
            subchapter= allchapters[idx]
            chapters=Selector(text=subchapter).xpath('//div[@class="zj_list autoHeight"]//div[@class="zj_list_con autoHeight"]/ul[@class="list_con_li autoHeight"]//li').extract()
            parts_name=Selector(text=subchapter).xpath('//div[@class="zj_list autoHeight"]//div[@class="zj_list_head"]/h2/text()').extract()[0]
            for chapter in chapters:
                chapter_name=None
                if len(Selector(text=chapter).xpath('//li/a//span[@class="list_con_zj"]/text()').extract())>0:
                    chapter_name=(parts_name+Selector(text=chapter).xpath('//li/a//span[@class="list_con_zj"]/text()').extract()[0]).strip()
                chapter_url=None
                if len(Selector(text=chapter).xpath('//li/a/@href').extract())>0:
                    chapter_url = 'http://www.930mh.com'+Selector(text=chapter).xpath('//li/a/@href').extract()[0]
                item_chapter = SpiderLoaderItem(item=ComicChapterItem(), response=response)
                item_chapter.add_value('batch_date', self.batch_date)
                item_chapter.add_value('manga_url', url)
                item_chapter.add_value('chapter_name', chapter_name)
                item_chapter.add_value('chapter_url', chapter_url)
                item_chapter.add_value('table_name', 'comic_chapter')
                yield item_chapter.load_item()