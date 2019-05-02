# -*- coding: UTF-8 -*-
import hashlib
import logging
import multiprocessing as mp
import requests
from spider.utils.mysqlutils import Mysql

def set_animation_imgage_url():
    animation_bangumi_list=Mysql().getAll("SELECT * FROM animation_bangumi where images=%s or images=%s ",['', '[]'])
    for animation_bangumi in animation_bangumi_list:
        new_img="[{'url': 'http://www.acgnfuns.com/images/full/nopicture.jpg', 'path': 'full/nopicture.jpg', 'checksum': ''}]"
        animation_bangumi_name = animation_bangumi['NAME']
        animation_bangumi_url = animation_bangumi['URL']
        animation_bangumi_tmp = Mysql().getMany("SELECT images FROM animation_bangumi where images!=%s and images!=%s and name like %s",1,['', '[]','%'+animation_bangumi_name+'%'])
        if animation_bangumi_tmp!=False:
            new_img=animation_bangumi_tmp[0]['images']
        Mysql().update("UPDATE animation_bangumi SET images = %s WHERE url = %s", [new_img,animation_bangumi_url])

def set_comic_imgage_url():
    comic_manga_list=Mysql().getAll("SELECT * FROM comic_manga where images=%s or images=%s ",['', '[]'])
    for comic_manga in comic_manga_list:
        new_img="[{'url': 'http://www.acgnfuns.com/images/full/nopicture.jpg', 'path': 'full/nopicture.jpg', 'checksum': ''}]"
        comic_manga_name = comic_manga['NAME']
        comic_manga_url = comic_manga['URL']
        comic_manga_tmp = Mysql().getMany("SELECT images FROM comic_manga where images!=%s and images!=%s and name like %s",1,['', '[]','%'+comic_manga_name+'%'])
        if comic_manga_tmp!=False:
            new_img=comic_manga_tmp[0]['images']
        Mysql().update("UPDATE comic_manga SET images = %s WHERE url = %s", [new_img,comic_manga_url])

def download_image_from_url(url,image_url,image_name,table):
    default_headers_dmzj = {
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
    # response = requests.get(image_url, stream=True, timeout=30, headers=default_headers_dmzj)
    # if response.ok:
    #     with open('../../images/full2/' + image_name, 'wb') as handle:
    #         for block in response.iter_content(1024):
    #             if not block:
    #                 break
    #             handle.write(block)
    # return response.ok,url,image_name,table
    return True, url, image_name, table

def write_image_from_url(result):
    # pass
    new_img = "[{'url': '"+result[1]+"', 'path': 'full/"+result[2]+"', 'checksum': ''}]"
    if result[0]:
        logging.warning('updating...')
        Mysql().update("UPDATE "+result[3]+" SET images = %s WHERE url = %s", [new_img, result[1]])

def get_image_by_url(table, host):
    pool = mp.Pool(processes=4)
    image_list = Mysql().getAll("SELECT * FROM "+table+" where host=%s and images not like %s", [host,'%www.dmzj.com%'])
    for image in image_list:
        image_url = image['IMG']
        url = image['URL'].decode()
        hash_object = hashlib.sha1(image_url)
        hex_dig = hash_object.hexdigest()
        image_name = hex_dig + '.jpg'
        pool.apply_async(download_image_from_url,args=(url,image_url,image_name,table),callback=write_image_from_url)
    pool.close()
    pool.join()

if __name__ == '__main__':
    get_image_by_url('comic_manga','www.dmzj.com')