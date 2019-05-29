# -*- coding: utf-8 -*-
import datetime
import re
import math
import scrapy
from spider.consts import DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF, MONGODB_ITEM_PIPELINES
from spider.items import SpiderLoaderItem, TagItem, EntryItem, PostItem
from spider.utils.httputils import convertRawString2Headers, convertRawString2Json, loadJsonValueByKey

class JuejinSpider(scrapy.Spider):
    name = "juejin"
    custom_settings = {
        'ITEM_PIPELINES': MONGODB_ITEM_PIPELINES,
        'SHOW_SQL': False,
        'DOWNLOADER_MIDDLEWARES': DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF,
        'DOWNLOAD_DELAY': 0.5
    }
    allowed_domains = ['juejin.im']
    batch_date = str(datetime.date.today())

    def start_requests(self):
        payload = {
        }
        headers = """Host: gold-tag-ms.juejin.im
                            Connection: keep-alive
                            X-Juejin-Src: web
                            X-Juejin-Client: 
                            Origin: https://juejin.im
                            X-Juejin-Token: 
                            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36
                            X-Juejin-Uid: 
                            Accept: */*
                            Referer: https://juejin.im/subscribe/all
                            Accept-Encoding: gzip, deflate, br
                            Accept-Language: en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,zh-CN;q=0.6,zh;q=0.5"""
        yield scrapy.Request(
            url='https://gold-tag-ms.juejin.im/v1/tags/type/hot/page/1/pageSize/1000',
            headers=convertRawString2Headers(headers), callback=self.parse_tags, dont_filter=True)

    def parse_tags(self, response):
        payload = {
        }
        headers = """Host: timeline-merger-ms.juejin.im
                        Connection: keep-alive
                        Origin: https://juejin.im
                        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36
                        Accept: */*
                        Referer: https://juejin.im/tag/%E5%89%8D%E7%AB%AF
                        Accept-Encoding: gzip, deflate, br
                        Accept-Language: en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,zh-CN;q=0.6,zh;q=0.5"""
        tags = convertRawString2Json(response.text).get('d').get('tags')
        for tag in tags:
            id = loadJsonValueByKey(tag, 'id')
            title = loadJsonValueByKey(tag, 'title')
            createdAt = loadJsonValueByKey(tag, 'createdAt')
            updatedAt = loadJsonValueByKey(tag, 'updatedAt')
            color = loadJsonValueByKey(tag, 'color')
            icon = loadJsonValueByKey(tag, 'icon')
            background = loadJsonValueByKey(tag, 'background')
            showOnNav = loadJsonValueByKey(tag, 'showOnNav')
            relationTagId = loadJsonValueByKey(tag, 'relationTagId')
            alias = loadJsonValueByKey(tag, 'alias')
            isCategory = loadJsonValueByKey(tag, 'isCategory')
            entryCount = loadJsonValueByKey(tag, 'entryCount')
            subscribersCount = loadJsonValueByKey(tag, 'subscribersCount')
            isSubscribe = loadJsonValueByKey(tag, 'isSubscribe')

            item = SpiderLoaderItem(item=TagItem(), response=response)
            item.add_value('batchDate', self.batch_date)
            item.add_value('id', id)
            item.add_value('title', title)
            item.add_value('createdAt', createdAt)
            item.add_value('updatedAt', updatedAt)
            item.add_value('color', color)
            item.add_value('icon', icon)
            item.add_value('background', background)
            item.add_value('showOnNav', showOnNav)
            item.add_value('relationTagId', relationTagId)
            item.add_value('alias', alias)
            item.add_value('isCategory', isCategory)
            item.add_value('entryCount', entryCount)
            item.add_value('subscribersCount', subscribersCount)
            item.add_value('isSubscribe', isSubscribe)
            item.add_value('tableName', 'juejinTag')
            yield item.load_item()

            yield scrapy.Request(
                url='https://timeline-merger-ms.juejin.im/v1/get_tag_entry?src=web&tagId='+tag['id']+'&page=0&pageSize=100&sort=rankIndex',
                headers=convertRawString2Headers(headers), meta={'tagId': tag['id']}, callback=self.parse_entry_total, dont_filter=True)

    def parse_entry_total(self, response):
        payload = {
        }
        headers = """Host: timeline-merger-ms.juejin.im
                                Connection: keep-alive
                                Origin: https://juejin.im
                                User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36
                                Accept: */*
                                Referer: https://juejin.im/tag/%E5%89%8D%E7%AB%AF
                                Accept-Encoding: gzip, deflate, br
                                Accept-Language: en-US,en;q=0.9,ja-JP;q=0.8,ja;q=0.7,zh-CN;q=0.6,zh;q=0.5"""
        response_json = convertRawString2Json(response.text)
        tag_id = response.meta['tagId']
        total = int(response_json.get('d').get('total'))
        for page in range(0,math.ceil(total/100)):
            yield scrapy.Request(
                url='https://timeline-merger-ms.juejin.im/v1/get_tag_entry?src=web&tagId='+tag_id+'&page='+str(page)+'&pageSize=100&sort=rankIndex',
                headers=convertRawString2Headers(headers), meta={'tagId': tag_id}, callback=self.parse_entry_list, dont_filter=True)

    def parse_entry_list(self, response):
        entrylist = convertRawString2Json(response.text).get('d').get('entrylist')
        for entry in entrylist:
            tagId = response.meta['tagId']
            collectionCount = loadJsonValueByKey(entry, 'collectionCount')
            userRankIndex = loadJsonValueByKey(entry, 'userRankIndex')
            buildTime = loadJsonValueByKey(entry, 'buildTime')
            commentsCount = loadJsonValueByKey(entry, 'commentsCount')
            gfw = loadJsonValueByKey(entry, 'gfw')
            objectId = loadJsonValueByKey(entry, 'objectId')
            checkStatus = loadJsonValueByKey(entry, 'checkStatus')
            isEvent = loadJsonValueByKey(entry, 'isEvent')
            entryView = loadJsonValueByKey(entry, 'entryView')
            subscribersCount = loadJsonValueByKey(entry, 'subscribersCount')
            ngxCachedTime = loadJsonValueByKey(entry, 'ngxCachedTime')
            verifyStatus = loadJsonValueByKey(entry, 'verifyStatus')
            tags = loadJsonValueByKey(entry, 'tags')
            updatedAt = loadJsonValueByKey(entry, 'updatedAt')
            rankIndex = loadJsonValueByKey(entry, 'rankIndex')
            hot = loadJsonValueByKey(entry, 'hot')
            autoPass = loadJsonValueByKey(entry, 'autoPass')
            originalUrl = loadJsonValueByKey(entry, 'originalUrl')
            verifyCreatedAt = loadJsonValueByKey(entry, 'verifyCreatedAt')
            createdAt = loadJsonValueByKey(entry, 'createdAt')
            user = loadJsonValueByKey(entry, 'user')
            author = loadJsonValueByKey(entry, 'author')
            screenshot = loadJsonValueByKey(entry, 'screenshot')
            original = loadJsonValueByKey(entry, 'original')
            hotIndex = loadJsonValueByKey(entry, 'hotIndex')
            content = loadJsonValueByKey(entry, 'content')
            title = loadJsonValueByKey(entry, 'title')
            lastCommentTime = loadJsonValueByKey(entry, 'lastCommentTime')
            type = loadJsonValueByKey(entry, 'type')
            english = loadJsonValueByKey(entry, 'english')
            category = loadJsonValueByKey(entry, 'category')
            viewsCount = loadJsonValueByKey(entry, 'viewsCount')
            summaryInfo = loadJsonValueByKey(entry, 'summaryInfo')
            eventInfo = loadJsonValueByKey(entry, 'eventInfo')
            isCollected = loadJsonValueByKey(entry, 'isCollected')

            item = SpiderLoaderItem(item=EntryItem(), response=response)
            item.add_value('batchDate', self.batch_date)
            item.add_value('tagId', tagId)
            item.add_value('collectionCount', collectionCount)
            item.add_value('userRankIndex', userRankIndex)
            item.add_value('buildTime', buildTime)
            item.add_value('commentsCount', commentsCount)
            item.add_value('gfw', gfw)
            item.add_value('objectId', objectId)
            item.add_value('checkStatus', checkStatus)
            item.add_value('isEvent', isEvent)
            item.add_value('entryView', entryView)
            item.add_value('subscribersCount', subscribersCount)
            item.add_value('ngxCachedTime', ngxCachedTime)
            item.add_value('verifyStatus', verifyStatus)
            item.add_value('tags', tags)
            item.add_value('updatedAt', updatedAt)
            item.add_value('rankIndex', rankIndex)
            item.add_value('hot', hot)
            item.add_value('autoPass', autoPass)
            item.add_value('originalUrl', originalUrl)
            item.add_value('verifyCreatedAt', verifyCreatedAt)
            item.add_value('createdAt', createdAt)
            item.add_value('user', user)
            item.add_value('author', author)
            item.add_value('screenshot', screenshot)
            item.add_value('original', original)
            item.add_value('hotIndex', hotIndex)
            item.add_value('content', content)
            item.add_value('title', title)
            item.add_value('lastCommentTime', lastCommentTime)
            item.add_value('type', type)
            item.add_value('english', english)
            item.add_value('category', category)
            item.add_value('viewsCount', viewsCount)
            item.add_value('summaryInfo', summaryInfo)
            item.add_value('eventInfo', eventInfo)
            item.add_value('isCollected', isCollected)
            item.add_value('tableName', 'juejinEntry')
            yield item.load_item()

            if 'juejin.im' not in originalUrl:
                continue
            yield scrapy.Request(
                url=originalUrl,
                headers={}, meta={'entryId': objectId}, callback=self.parse_post, dont_filter=True)

    def parse_post(self, response):
        entryId = response.meta['entryId']
        post = ''.join(response.xpath('//article//text()').extract()).strip()
        pattern = re.compile('^(?:[\t ]*(?:\r?\n|\r))+')
        post = pattern.sub('', post)

        item = SpiderLoaderItem(item=PostItem(), response=response)
        item.add_value('batchDate', self.batch_date)
        item.add_value('entryId', entryId)
        item.add_value('post', post)
        item.add_value('tableName', 'juejinPost')
        yield item.load_item()

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