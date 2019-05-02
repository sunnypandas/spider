# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy import Selector

from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_ON, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, ComicMangaItem, ComicChapterItem


class MH66Spider(scrapy.Spider):
    name = "66mh"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_ON,
        'DOWNLOAD_DELAY': 3
    }
    allowed_domains = ['www.66mh.cc']
    batch_date = datetime.datetime.now().date()
    default_data = {

    }
    default_data = urllib.parse.urlencode(default_data)
    default_headers = {
        'Host': 'www.66mh.cc',
        'Proxy-Connection': 'keep-alive',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': 'http://www.66mh.cc/list/rexue/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5,zh-TW;q=0.4',
        'Cookie': 'bdshare_firstime=1518665728994; UM_distinctid=161978809ef85-08aab345d58772-3e3d5100-144000-161978809f115b; CNZZDATA1260083709=833767502-1518660398-null%7C1522763783; Hm_lvt_e77d6093d23ee87d64a51c8c1f6695da=1522728990,1522765765,1522835615,1522841056; Hm_lpvt_e77d6093d23ee87d64a51c8c1f6695da=1522841078'
    }
    def start_requests(self):
        for url in ['http://www.66mh.cc/list/rexue/','http://www.66mh.cc/list/gedou/','http://www.66mh.cc/list/kehuan/','http://www.66mh.cc/list/jingji/','http://www.66mh.cc/list/gaoxiao/','http://www.66mh.cc/list/tuili/','http://www.66mh.cc/list/kongbu/','http://www.66mh.cc/list/danmei/','http://www.66mh.cc/list/shaonv/','http://www.66mh.cc/list/xiee/','http://www.66mh.cc/list/shenghuo/','http://www.66mh.cc/list/qita/']:
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, callback=self.get_fake_url, meta={'base_url':url}, dont_filter=True)

    def get_fake_url(self, response):
        url= response.meta['base_url']+response.xpath('//div[@id="pager"]//a[last()]/@href').extract()[0]
        yield scrapy.Request(
            url=url,
            headers=self.default_headers, body=self.default_data, callback=self.get_final_url, meta={'base_url':response.meta['base_url']}, dont_filter=True)
    def get_final_url(self, response):
        total_page = response.xpath('//div[@id="pager"]/span[@class="total"]/strong/text()').extract()[0]
        pages = int(total_page)
        url=response.meta['base_url']
        for page in range(1,pages+1):
            #time.sleep(random.uniform(3, 5))
            yield scrapy.Request(
                url=url+str(page)+'.html',
                headers=self.default_headers, body=self.default_data, callback=self.parse_basic_info, dont_filter=True)

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@class="dmList clearfix"]/ul//li').extract()
        for content in contents:
            img = Selector(text=content).xpath('//li/p[@class="fl cover"]/a[@class="pic"]/img/@src').extract()[0]
            if not (img!='' and img!=None and img.startswith('http')):
                img='http://www.66mh.cc'+img
            name = Selector(text=content).xpath('//li/p[@class="fl cover"]/a[@class="pic"]/img/@alt').extract()[0]
            url = 'http://www.66mh.cc'+Selector(text=content).xpath('//li/p[@class="fl cover"]/a[@class="pic"]/@href').extract()[0]
            status_part1=''
            if len(Selector(text=content).xpath('//li/p[@class="fl cover"]/span/a/text()').extract())>0:
                status_part1 = Selector(text=content).xpath('//li/p[@class="fl cover"]/span/a/text()').extract()[0]
            update_time=None
            if len(Selector(text=content).xpath('//li/dl/dd//p[1]/span/text()').extract())>0:
                update_time=Selector(text=content).xpath('//li/dl/dd//p[1]/span/text()').extract()[0]
            else:
                update_time = Selector(text=content).xpath('//li/dl/dd//p[1]/span/font/text()').extract()[0]
            status_part2 = ''
            if len(Selector(text=content).xpath('//li/dl/dd//p[2]/span/text()').extract()) > 0:
                status_part2 = Selector(text=content).xpath('//li/dl/dd//p[2]/span/text()').extract()[0]
            status=status_part2+status_part1
            type=None
            if len(Selector(text=content).xpath('//li/dl/dd//p[3]/a/text()').extract()) > 0:
                type = Selector(text=content).xpath('//li/dl/dd//p[3]/a/text()').extract()[0]
            yield scrapy.Request(
                url=url,
                headers=self.default_headers, body=self.default_data, meta={'img': img,'name': name,'update_time': update_time,'status': status,'type': type}, callback=self.parse_detail_info, dont_filter=True)
    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name = response.meta['name']
        update_time = response.meta['update_time']
        status = response.meta['status']
        type = response.meta['type']
        author_names=None
        if len(response.xpath('//div[@class="intro_l"]//div[@class="info"]//p[@class="w260"][2]/text()').extract()):
            author_names = response.xpath('//div[@class="intro_l"]//div[@class="info"]//p[@class="w260"][2]/text()').extract()[0]
        show_date = response.xpath('//div[@class="intro_l"]//div[@class="info"]//p[@class="w260"][3]/text()').extract()[0]
        introduction=None
        if len(response.xpath('//div[@class="introduction"]//p[1]/text()').extract())>0:
            introduction = response.xpath('//div[@class="introduction"]//p[1]/text()').extract()[0]
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
        item_manga.add_value('show_date', show_date)
        item_manga.add_value('update_time', update_time)
        item_manga.add_value('table_name', 'comic_manga')
        yield item_manga.load_item()

        chapters=response.xpath('//div[@class="plist pnormal"]/ul//li').extract()
        for chapter in chapters:
            chapter_name=None
            if len(Selector(text=chapter).xpath('//li/a/@title').extract())>0:
                chapter_name=Selector(text=chapter).xpath('//li/a/@title').extract()[0]
            chapter_url=None
            if len(Selector(text=chapter).xpath('//li/a/@href').extract())>0:
                chapter_url = 'http://www.66mh.cc'+Selector(text=chapter).xpath('//li/a/@href').extract()[0]
            item_chapter = SpiderLoaderItem(item=ComicChapterItem(), response=response)
            item_chapter.add_value('batch_date', self.batch_date)
            item_chapter.add_value('manga_url', url)
            item_chapter.add_value('chapter_name', chapter_name)
            item_chapter.add_value('chapter_url', chapter_url)
            item_chapter.add_value('table_name', 'comic_chapter')
            yield item_chapter.load_item()