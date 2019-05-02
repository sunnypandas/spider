# -*- coding: utf-8 -*-
import datetime
import urllib

import scrapy
from scrapy.spiders.init import InitSpider
from scrapy import Selector
from scrapy_splash import SplashRequest
from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MYSQL_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, NovelNoberuItem, NovelChapterItem


class Wenku8Spider(InitSpider):
    name = "wenku8"
    custom_settings = {
        'ITEM_PIPELINES': MYSQL_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF,
        #'DOWNLOAD_DELAY': 3
    }
    allowed_domains = ['www.wenku8.com']
    batch_date = datetime.datetime.now().date()

    def init_request(self):
        """This function is called before crawling starts."""
        return scrapy.Request(url='http://www.wenku8.com/login.php?do=submit&jumpurl=http%3A%2F%2Fwww.wenku8.com%2Fmodules%2Farticle%2Farticlelist.php', callback=self.login)

    def login(self, response):
        """Generate a login request."""
        return scrapy.FormRequest.from_response(response,
                                         formdata={'username': '', 'password': '','usecookie': '0','action': 'login','submit': '%26%23160%3B%B5n%26%23160%3B%26%23160%3B%BF%FD%26%23160%3B'},
                                         callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are successfully logged in.
        """
        if 'sppsun' in response.text:
            self.logger.info("Successfully logged in. Let's start crawling!")
            pages=self.get_final_url(response)
            for page in range(1, pages + 1):
                yield scrapy.Request(url='http://www.wenku8.com/modules/article/articlelist.php?page=' + str(page),
                                     callback=self.parse_basic_info, dont_filter=True)
            # Now the crawling can begin..
            return self.initialized()
        else:
            self.logger.info("Login failed!")

    def get_final_url(self, response):
        total_page = response.xpath('//em[@id="pagestats"]/text()').extract()[0].split('/')[1]
        pages = int(total_page)
        return pages

    def parse_basic_info(self, response):
        contents=response.xpath('//div[@style="width:373px;float:left;margin:5px 0px 5px 5px;"]').extract()
        for content in contents:
            img = Selector(text=content).xpath('//div[@style="width:373px;float:left;margin:5px 0px 5px 5px;"]/div[@style="width:95px;float:left;"]/a/img/@src').extract()[0]
            if not img.startswith('http'):
                img='http://www.wenku8.com'+img
            url=Selector(text=content).xpath('//div[@style="width:373px;float:left;margin:5px 0px 5px 5px;"]/div[@style="width:95px;float:left;"]/a/@href').extract()[0]
            name = Selector(text=content).xpath('//div[@style="width:373px;float:left;margin:5px 0px 5px 5px;"]/div[@style="width:95px;float:left;"]/a/@title').extract()[0]
            yield scrapy.Request(url=url, meta={'img':img,'name':name}, callback=self.parse_detail_info, dont_filter=True)

    def parse_detail_info(self, response):
        url=response.url
        img=response.meta['img']
        name = response.meta['name']
        author_names=''
        if len(response.xpath('//div[@id="content"]//table[1]/tr[2]/td[2]/text()').extract())>0:
            author_names = response.xpath('//div[@id="content"]//table[1]/tr[2]/td[2]/text()').extract()[0].split('：')[1]
        size=''
        if len(response.xpath('//div[@id="content"]//table[1]/tr[2]/td[5]/text()').extract())>0:
            size = response.xpath('//div[@id="content"]//table[1]/tr[2]/td[5]/text()').extract()[0].split('：')[1]
        status_part1=''
        if len(response.xpath('//div[@id="content"]//table[1]/tr[2]/td[3]/text()').extract())>0:
            status_part1=response.xpath('//div[@id="content"]//table[1]/tr[2]/td[3]/text()').extract()[0].split('：')[1]
        length=len(response.xpath('//div[@id="content"]//table[2]/tr[1]/td[2]/span[@style="font-size:14px;"]').extract())
        introduction = ''
        status_part2 = ''
        if length==2:
            if len(response.xpath('//div[@id="content"]//table[2]/tr[1]/td[2]/span[@style="font-size:14px;"][2]').extract()) > 0:
                introduction = response.xpath('//div[@id="content"]//table[2]/tr[1]/td[2]/span[@style="font-size:14px;"][2]').extract()[0]
            if len(response.xpath('//div[@id="content"]//table[2]/tr[1]/td[2]/span[@style="font-size:14px;"][1]/a/text()').extract())>0:
                status_part2 = response.xpath('//div[@id="content"]//table[2]/tr[1]/td[2]/span[@style="font-size:14px;"][1]/a/text()').extract()[0]
        elif length==1:
            if len(response.xpath('//div[@id="content"]//table[2]/tr[1]/td[2]/span[@style="font-size:14px;"][1]').extract()) > 0:
                introduction = response.xpath('//div[@id="content"]//table[2]/tr[1]/td[2]/span[@style="font-size:14px;"][1]').extract()[0]
        status=status_part1+status_part2
        update_time=''
        if len(response.xpath('//div[@id="content"]//table[1]/tr[2]/td[4]/text()').extract())>0:
            update_time = response.xpath('//div[@id="content"]//table[1]/tr[2]/td[4]/text()').extract()[0].split('：')[1]
        type=''
        if len(response.xpath('//div[@id="content"]//table[1]/tr[2]/td[1]/text()').extract())>0:
            type = response.xpath('//div[@id="content"]//table[1]/tr[2]/td[1]/text()').extract()[0].split('：')[1]
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
        if len(response.xpath('//div[@style="width:580px;margin:0px auto;"]//span[1]/fieldset[1]/div/a/@href').extract()) > 0:
            tmp_url = response.xpath('//div[@style="width:580px;margin:0px auto;"]//span[1]/fieldset[1]/div/a/@href').extract()[0]
            yield scrapy.Request(url=tmp_url, meta={'noberu_url': url}, callback=self.parse_chapter_info, dont_filter=True)

    def parse_chapter_info(self, response):
        noberu_url=response.meta['noberu_url']
        chapters=response.xpath('//table[@class="css"]/tr').extract()
        part_name = ''
        for chapter in chapters:
            tr_part=Selector(text=chapter).xpath('//tr/td[@class="vcss"][1]/text()').extract()
            if len(tr_part)>0:
                part_name=tr_part[0]
            tr_chapters = Selector(text=chapter).xpath('//tr/td[@class="ccss"]').extract()
            for tr_chapter in tr_chapters:
                chapter_name=''
                if len(Selector(text=tr_chapter).xpath('//td[@class="ccss"]/a/text()').extract())>0:
                    chapter_name = part_name+Selector(text=tr_chapter).xpath('//td[@class="ccss"]/a/text()').extract()[0]
                chapter_url = ''
                if len(Selector(text=tr_chapter).xpath('//td[@class="ccss"]/a/@href').extract())>0:
                    chapter_url = response.url[0:-9]+Selector(text=tr_chapter).xpath('//td[@class="ccss"]/a/@href').extract()[0]
                if chapter_name!='' and chapter_url!='':
                    item_chapter = SpiderLoaderItem(item=NovelChapterItem(), response=response)
                    item_chapter.add_value('batch_date', self.batch_date)
                    item_chapter.add_value('noberu_url', noberu_url)
                    item_chapter.add_value('chapter_name', chapter_name)
                    item_chapter.add_value('chapter_url', chapter_url)
                    item_chapter.add_value('table_name', 'novel_chapter')
                    yield item_chapter.load_item()