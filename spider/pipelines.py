# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import pymysql.cursors
import redis
from twisted.enterprise import adbapi
import logging
import ibm_db_dbi
import ibm_db
class MySqlPipeline(object):
    def __init__(self, dbpool, conn):
        self.dbpool = dbpool
        self.conn = conn
    show_sql = False
    @classmethod
    def from_settings(cls, settings):
        '''
        读取配置文件中的数据库配置
        :param settings:
        :return:
        '''
        global show_sql
        show_sql = settings['SHOW_SQL']
        dbpool = adbapi.ConnectionPool(
            'pymysql',
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            db=settings['MYSQL_DBNAME'],
            charset=settings['MYSQL_CHARSET'],
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True
        )
        conn = redis.StrictRedis(
            host=settings['REDIS_HOST'],
            port=settings['REDIS_PORT'],
            db=settings['REDIS_DB']
        )
        return cls(dbpool, conn)

    def process_item(self, item, spider):
        '''
        处理ITEM
        :param item:
        :param spider:
        :return:
        '''
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)
        return item

    def handle_error(self, failure):
        '''
        添加error操作
        :param failure:
        :return:
        '''
        logging.info('%s', failure)

    def do_insert(self, cursor, item):
        '''
        添加详细信息
        :param cursor:
        :param item:
        :return:
        '''
        insert = 'insert into '+item['table_name']+' ('
        value = 'values('
        keys = list(item)
        if 'table_name' in item:
            keys.remove('table_name')
        for i in range(0, len(keys)):
            if i == (len(keys) - 1):
                insert = insert + keys[i] + ')'
                value = value + '\"' + str(item[keys[i]]).replace("\"", "\'") + '\")'
            else:
                insert = insert + keys[i] + ','
                value = value + '\"' + str(item[keys[i]]).replace("\"", "\'") + '\",'
        sql = insert + value
        if show_sql == True:
            logging.info('%s', sql)
        try:
            cursor.execute(sql)
        except RuntimeError:
            logging.warning('Sql command executing error: %s', sql)
            logging.warning('The error is: %s', RuntimeError)


class DB2Pipeline(object):
    def __init__(self, dbpool, conn):
        self.dbpool = dbpool
        self.conn = conn
    show_sql=False
    @classmethod
    def from_settings(cls, settings):
        '''
        读取配置文件中的数据库配置
        :param settings:
        :return:
        '''
        global show_sql
        show_sql = settings['SHOW_SQL']
        dbpool = adbapi.ConnectionPool(
            'ibm_db_dbi',
            dsn='DATABASE='+settings['DB2_DBNAME']+';HOSTNAME='+settings['DB2_HOST']+';UID='+settings['DB2_USER']+';PWD='+settings['DB2_PASSWORD']+';PORT='+str(settings['DB2_PORT']),
            conn_options={'SQL_ATTR_AUTOCOMMIT':ibm_db.SQL_AUTOCOMMIT_ON}
        )
        conn = redis.StrictRedis(
            host=settings['REDIS_HOST'],
            port=settings['REDIS_PORT'],
            db=settings['REDIS_DB']
        )
        return cls(dbpool, conn)

    def process_item(self, item, spider):
        '''
        处理ITEM
        :param item:
        :param spider:
        :return:
        '''
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)
        return item

    def handle_error(self, failure):
        '''
        添加error操作
        :param failure:
        :return:
        '''
        logging.warning('%s', failure)

    def do_insert(self, cursor, item):
        '''
        添加详细信息
        :param cursor:
        :param item:
        :return:
        '''
        insert = 'insert into ' + item['table_name'] + ' ('
        value = 'values('
        keys = list(item)
        if 'table_name' in item:
            keys.remove('table_name')
        for i in range(0, len(keys)):
            if i == (len(keys) - 1):
                insert = insert + keys[i] + ')'
                value = value + '\'' + str(item[keys[i]]).replace("\'", "\"") + '\')'
            else:
                insert = insert + keys[i] + ','
                value = value + '\'' + str(item[keys[i]]).replace("\'", "\"") + '\','
        sql = insert + value
        if show_sql == True:
            logging.info('%s', sql)
        try:
            cursor.execute(sql)
        except RuntimeError:
            logging.warning('Sql command executing error: %s', sql)
            logging.warning('The error is: %s', RuntimeError)
