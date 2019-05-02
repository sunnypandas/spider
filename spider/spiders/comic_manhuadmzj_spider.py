# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from flask import json
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, \
    MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, ComicMangaItem, ComicChapterItem


class Manhuadmzj(scrapy.Spider):
    name = "manhuadmzj"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF
    }
    allowed_domains = ['manhua.dmzj.com']
    batch_date = datetime.datetime.now().date()
    default_data = {
        'c':'category',
        'm':'doSearch',
        'status':0,
        'reader_group':0,
        'zone':0,
        'initial':'all',
        'type':0,
        'p':1,
        'callback':'search.renderResult'
    }
    #default_data = urllib.parse.urlencode(default_data)
    #default_data = json.dumps(default_data)
    default_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5',
        #'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'Cookie': 'Hm_lvt_645dcc265dc58142b6dbfea748247f02=1520074323; show_tip_1=0; UM_distinctid=161eb7d828c19b-0c068bc78911e4-3e3d5f01-144000-161eb7d828d13f',
        'Referer': 'https://manhua.dmzj.com/tags/category_search/0-0-0-all-0-0-0-1.shtml',
        'Connection': 'keep-alive',
        'Host': 'sacg.dmzj.com'
    }
    def start_requests(self):
        yield scrapy.Request(
            url='https://sacg.dmzj.com/mh/index.php?c=category&m=doSearch&status=0&reader_group=0&zone=0&initial=all&type=0&p=1&callback=search.renderResult',
            headers=self.default_headers, body=urllib.parse.urlencode(self.default_data), callback=self.get_final_url, dont_filter=True)

    def get_final_url(self, response):
        contents = json.loads(response.text[20:-2])
        total_page = contents['page_count']
        pages=int(total_page)
        for page in range(1,pages+1):
            #time.sleep(random.uniform(3, 5))
            self.default_data['p']=page
            yield scrapy.Request(
                url='https://sacg.dmzj.com/mh/index.php?c=category&m=doSearch&status=0&reader_group=0&zone=0&initial=all&type=0&p='+str(page)+'&callback=search.renderResult',
                headers=self.default_headers, body=urllib.parse.urlencode(self.default_data), callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=json.loads(response.text[20:-2])['result']
        for content in contents:
            url=None
            if not content['comic_url'].startswith('http'):
                url = 'https://manhua.dmzj.com'+content['comic_url']
            else:
                url = content['comic_url']
            img = 'https:'+content['comic_cover']
            name = content['name']
            author_names=content['author']
            type = content['author']
            status_part1=''
            if len(Selector(text=content['status']).xpath('//span/text()').extract())>0:
                status_part1 = Selector(text=content['status']).xpath('//span/text()').extract()[0]
            status_part2 = content['last_chapter']
            status=status_part1+status_part2
            update_time=content['last_update_date']
            if not content['comic_url'].startswith('http'):
                yield scrapy.Request(
                    url=url,
                    headers={}, body=urllib.parse.urlencode({}), callback=self.parse_detail_info, meta={'img':img,'name':name,'author_names':author_names,'type':type,'status':status,'update_time':update_time}, dont_filter=True)
            else:
                yield scrapy.Request(
                    url=url,
                    headers={}, body=urllib.parse.urlencode({}), callback=self.parse_other_detail_info,
                    meta={'img': img, 'name': name, 'author_names': author_names, 'type': type, 'status': status,
                          'update_time': update_time}, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name = response.meta['name']
        author_names = response.meta['author_names']
        type = response.meta['type']
        status = response.meta['status']
        update_time = response.meta['update_time']
        area_names=None
        if len(response.xpath('//div[@class="anim-main_list"]/table//tr[4]/td/a/text()').extract())>0:
            area_names=response.xpath('//div[@class="anim-main_list"]/table//tr[4]/td/a/text()').extract()[0]
        introduction=''
        if len(response.xpath('//div[@class="middleright_mr margin_top_10px"]//div[@class="line_height_content"]').extract())>0:
            introduction = response.xpath('//div[@class="middleright_mr margin_top_10px"]//div[@class="line_height_content"]').extract()[0]
        item_manga = SpiderLoaderItem(item=ComicMangaItem(image_urls=[img]), response=response)
        item_manga.add_value('batch_date', self.batch_date)
        item_manga.add_value('host', self.allowed_domains[0])
        item_manga.add_value('url', url)
        item_manga.add_value('img', img)
        item_manga.add_value('name', name)
        item_manga.add_value('author_names', author_names)
        item_manga.add_value('area_names', area_names)
        item_manga.add_value('status', status)
        item_manga.add_value('type', type)
        item_manga.add_value('introduction', introduction)
        item_manga.add_value('update_time', update_time)
        item_manga.add_value('table_name', 'comic_manga')
        yield item_manga.load_item()

        allpages=response.xpath('//div[@class="middleright_mr"]//div[@class="cartoon_online_border"]').extract()
        otherpages = response.xpath('//div[@class="middleright_mr"]//div[@class="cartoon_online_border_other"]').extract()
        size=len(allpages)
        othersize = len(otherpages)
        for idx in range(0,size):
            subpage= allpages[idx]
            chapters=Selector(text=subpage).xpath('//div[@class="cartoon_online_border"]/ul//li').extract()
            for chapter in chapters:
                chapter_name=None
                if len(Selector(text=chapter).xpath('//li/a/text()').extract())>0:
                    chapter_name=Selector(text=chapter).xpath('//li/a/text()').extract()[0]
                chapter_url=None
                if len(Selector(text=chapter).xpath('//li/a/@href').extract())>0:
                    chapter_url = 'https://manhua.dmzj.com'+Selector(text=chapter).xpath('//li/a/@href').extract()[0]
                item_chapter = SpiderLoaderItem(item=ComicChapterItem(), response=response)
                item_chapter.add_value('batch_date', self.batch_date)
                item_chapter.add_value('manga_url', url)
                item_chapter.add_value('chapter_name', chapter_name)
                item_chapter.add_value('chapter_url', chapter_url)
                item_chapter.add_value('table_name', 'comic_chapter')
                yield item_chapter.load_item()

        for idx in range(0,othersize):
            subpage= otherpages[idx]
            chapters=Selector(text=subpage).xpath('//div[@class="cartoon_online_border_other"]/ul//li').extract()
            for chapter in chapters:
                chapter_name=None
                if len(Selector(text=chapter).xpath('//li/a/text()').extract())>0:
                    chapter_name=Selector(text=chapter).xpath('//li/a/text()').extract()[0]
                chapter_url=None
                if len(Selector(text=chapter).xpath('//li/a/@href').extract())>0:
                    chapter_url = 'https://manhua.dmzj.com'+Selector(text=chapter).xpath('//li/a/@href').extract()[0]
                item_chapter = SpiderLoaderItem(item=ComicChapterItem(), response=response)
                item_chapter.add_value('batch_date', self.batch_date)
                item_chapter.add_value('manga_url', url)
                item_chapter.add_value('chapter_name', chapter_name)
                item_chapter.add_value('chapter_url', chapter_url)
                item_chapter.add_value('table_name', 'comic_chapter')
                yield item_chapter.load_item()

    def parse_other_detail_info(self, response):
        url = response.url
        img = response.meta['img']
        name = response.meta['name']
        author_names = response.meta['author_names']
        type = response.meta['type']
        status = response.meta['status']
        update_time = response.meta['update_time']
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
        item_manga.add_value('update_time', update_time)
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