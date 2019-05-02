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

class PubPermissionsNameItem(scrapy.Item):
    # define the fields for your item here like:
    batch_date=scrapy.Field()
    cust_name = scrapy.Field()
    adm_license_writ_no = scrapy.Field()
    audit_type=scrapy.Field()
    legal_person=scrapy.Field()
    content=scrapy.Field()
    permit_validity=scrapy.Field()
    permit_decision_date=scrapy.Field()
    permit_issue_date=scrapy.Field()
    local_code=scrapy.Field()
    permit_org=scrapy.Field()
    data_update_date=scrapy.Field()
    table_name=scrapy.Field()

class RecordParamRedItem(scrapy.Item):
    batch_date = scrapy.Field()
    cust_name = scrapy.Field()
    data_source=scrapy.Field()
    no = scrapy.Field()
    taxpayer_name = scrapy.Field()
    rating_year = scrapy.Field()
    data_update_date = scrapy.Field()
    table_name = scrapy.Field()

class RecordParamAttentionItem(scrapy.Item):
    batch_date = scrapy.Field()
    cust_name = scrapy.Field()
    data_source = scrapy.Field()
    comp_name = scrapy.Field()
    reg_no = scrapy.Field()
    legal_person = scrapy.Field()
    exception_reason_type = scrapy.Field()
    set_date = scrapy.Field()
    org_name = scrapy.Field()
    data_update_date = scrapy.Field()
    table_name = scrapy.Field()

class DishonestyBlacklistItem(scrapy.Item):
    batch_date = scrapy.Field()
    cust_name = scrapy.Field()
    data_source = scrapy.Field()
    case_no = scrapy.Field()
    dishonesty_cust_name = scrapy.Field()
    legal_person = scrapy.Field()
    exec_court = scrapy.Field()
    area_name = scrapy.Field()
    exec_gist_no = scrapy.Field()
    exec_gist_org = scrapy.Field()
    writ_content = scrapy.Field()
    performance_status = scrapy.Field()
    dishonesty_cust_specific_status = scrapy.Field()
    issue_date = scrapy.Field()
    register_date = scrapy.Field()
    performanced_part = scrapy.Field()
    unperformanced_part = scrapy.Field()
    data_update_date = scrapy.Field()
    table_name = scrapy.Field()

class SeriousRevenueLawlessCustListItem(scrapy.Item):
    batch_date = scrapy.Field()
    cust_name = scrapy.Field()
    data_source = scrapy.Field()
    taxer_name = scrapy.Field()
    taxer_id = scrapy.Field()
    org_code = scrapy.Field()
    register_addr = scrapy.Field()
    legal_person_name = scrapy.Field()
    financing_person_name = scrapy.Field()
    intermediary_info = scrapy.Field()
    case_nature = scrapy.Field()
    lawless_fact = scrapy.Field()
    punish_status = scrapy.Field()
    case_report_date = scrapy.Field()
    data_update_date = scrapy.Field()
    table_name = scrapy.Field()

class PurchasingBadnessRecordItem(scrapy.Item):
    batch_date = scrapy.Field()
    cust_name = scrapy.Field()
    data_source = scrapy.Field()
    supplier_name = scrapy.Field()
    supplier_addr = scrapy.Field()
    lawless_status = scrapy.Field()
    punish_result = scrapy.Field()
    punish_gist = scrapy.Field()
    punish_date = scrapy.Field()
    exec_org = scrapy.Field()
    punish_end_date = scrapy.Field()
    data_update_date = scrapy.Field()
    table_name = scrapy.Field()

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