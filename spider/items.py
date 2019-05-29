# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join


def delete_space(value):
    '''
    删除字符串中的所有空格
    :param value:
    :return:
    '''
    return str(value).replace(' ', '').strip()


def delete_plus(value):
    '''
    删除字符串中的"+"
    :param value:
    :return:
    '''
    return str(value).replace('+', '').strip()


def date_parse(value):
    '''
    转换为日期类型
    :param value:
    :return:
    '''
    try:
        value = value.replace('·', '').replace('/', '').strip()
        value = datetime.datetime.strptime(value, '%Y%m%d').date()
    except Exception as e:
        value = datetime.datetime.now().date()
    return str(value)


def return_value(value):
    '''
    保持原来的数值不变
    :param value:
    :return:
    '''
    return str(value).strip()


def get_value(value):
    '''
    通过正则表达式获取特定值
    :param value:
    :return:
    '''
    value = str(value).strip()
    obj = re.match('.*\[(.*?)\].*', value)
    if obj:
        return obj.group(1)
    else:
        return value
class SpiderLoaderItem(ItemLoader):
    '''
    自定义ITEM，取每个字段数组的第一个值
    '''
    default_output_processor = TakeFirst()

###########################################################################
class ProxyListItem(scrapy.Item):
    batch_date = scrapy.Field()
    ip = scrapy.Field()
    port = scrapy.Field()
    proxy = scrapy.Field()
    anonymous = scrapy.Field()
    table_name = scrapy.Field()

class BankListItem(scrapy.Item):
    type = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()
    address = scrapy.Field()
    tel = scrapy.Field()
    workday = scrapy.Field()
    table_name = scrapy.Field()

class AnimationBangumiItem(scrapy.Item):
    batch_date = scrapy.Field()
    host = scrapy.Field()
    url = scrapy.Field()
    img = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    name = scrapy.Field()
    author_names = scrapy.Field()
    actor_names = scrapy.Field()
    director_names = scrapy.Field()
    show_date = scrapy.Field()
    area_names = scrapy.Field()
    language = scrapy.Field()
    status = scrapy.Field()
    type = scrapy.Field()
    introduction = scrapy.Field()
    update_time = scrapy.Field()
    table_name = scrapy.Field()

class AnimationEpisodeItem(scrapy.Item):
    batch_date = scrapy.Field()
    bangumi_url = scrapy.Field()
    episode_name = scrapy.Field()
    episode_url = scrapy.Field()
    playee_name = scrapy.Field()
    playee_url = scrapy.Field()
    table_name = scrapy.Field()

class ComicMangaItem(scrapy.Item):
    batch_date = scrapy.Field()
    host = scrapy.Field()
    url = scrapy.Field()
    img = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    name = scrapy.Field()
    author_names = scrapy.Field()
    show_date = scrapy.Field()
    area_names = scrapy.Field()
    language = scrapy.Field()
    status = scrapy.Field()
    type = scrapy.Field()
    introduction = scrapy.Field()
    update_time = scrapy.Field()
    table_name = scrapy.Field()

class ComicChapterItem(scrapy.Item):
    batch_date = scrapy.Field()
    manga_url = scrapy.Field()
    chapter_name = scrapy.Field()
    chapter_url = scrapy.Field()
    table_name = scrapy.Field()

class GameGeimuItem(scrapy.Item):
    batch_date = scrapy.Field()
    host = scrapy.Field()
    url = scrapy.Field()
    img = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    name = scrapy.Field()
    zh_name = scrapy.Field()
    en_name = scrapy.Field()
    creator_name = scrapy.Field()
    publisher_name = scrapy.Field()
    area_names = scrapy.Field()
    language = scrapy.Field()
    status = scrapy.Field()
    type = scrapy.Field()
    update_time = scrapy.Field()
    publish_date = scrapy.Field()
    show_date = scrapy.Field()
    size = scrapy.Field()
    category = scrapy.Field()
    introduction = scrapy.Field()
    table_name = scrapy.Field()

class GameDownloadItem(scrapy.Item):
    batch_date = scrapy.Field()
    geimu_url = scrapy.Field()
    download_name = scrapy.Field()
    download_url = scrapy.Field()
    table_name = scrapy.Field()

class NovelNoberuItem(scrapy.Item):
    batch_date = scrapy.Field()
    host = scrapy.Field()
    url = scrapy.Field()
    img = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    name = scrapy.Field()
    author_names = scrapy.Field()
    area_names = scrapy.Field()
    language = scrapy.Field()
    status = scrapy.Field()
    type = scrapy.Field()
    update_time = scrapy.Field()
    size = scrapy.Field()
    category = scrapy.Field()
    introduction = scrapy.Field()
    table_name = scrapy.Field()

class NovelChapterItem(scrapy.Item):
    batch_date = scrapy.Field()
    noberu_url = scrapy.Field()
    chapter_name = scrapy.Field()
    chapter_url = scrapy.Field()
    table_name = scrapy.Field()

class TagItem(scrapy.Item):
    batchDate = scrapy.Field()
    id = scrapy.Field()
    title = scrapy.Field()
    createdAt = scrapy.Field()
    updatedAt = scrapy.Field()
    color = scrapy.Field()
    icon = scrapy.Field()
    background = scrapy.Field()
    showOnNav = scrapy.Field()
    relationTagId = scrapy.Field()
    alias = scrapy.Field()
    isCategory = scrapy.Field()
    entryCount = scrapy.Field()
    subscribersCount = scrapy.Field()
    isSubscribe = scrapy.Field()
    tableName = scrapy.Field()

class EntryItem(scrapy.Item):
    batchDate = scrapy.Field()
    tagId = scrapy.Field()
    collectionCount = scrapy.Field()
    userRankIndex = scrapy.Field()
    buildTime = scrapy.Field()
    commentsCount = scrapy.Field()
    gfw = scrapy.Field()
    objectId = scrapy.Field()
    checkStatus = scrapy.Field()
    isEvent = scrapy.Field()
    entryView = scrapy.Field()
    subscribersCount = scrapy.Field()
    ngxCachedTime = scrapy.Field()
    verifyStatus = scrapy.Field()
    tags = scrapy.Field()
    updatedAt = scrapy.Field()
    rankIndex = scrapy.Field()
    hot = scrapy.Field()
    autoPass = scrapy.Field()
    originalUrl = scrapy.Field()
    verifyCreatedAt = scrapy.Field()
    createdAt = scrapy.Field()
    user = scrapy.Field()
    author = scrapy.Field()
    screenshot = scrapy.Field()
    original = scrapy.Field()
    hotIndex = scrapy.Field()
    content = scrapy.Field()
    title = scrapy.Field()
    lastCommentTime = scrapy.Field()
    type = scrapy.Field()
    english = scrapy.Field()
    category = scrapy.Field()
    viewsCount = scrapy.Field()
    summaryInfo = scrapy.Field()
    eventInfo = scrapy.Field()
    isCollected = scrapy.Field()
    tableName = scrapy.Field()

class PostItem(scrapy.Item):
    batchDate = scrapy.Field()
    entryId = scrapy.Field()
    post = scrapy.Field()
    tableName = scrapy.Field()