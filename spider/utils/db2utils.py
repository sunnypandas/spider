#-*- coding: utf-8 -*-
"""
数据库管理类
"""
import ibm_db_dbi
import ibm_db
from DBUtils.PooledDB import PooledDB
from scrapy.utils.project import get_project_settings

#数据库实例化类
from singleton.singleton import Singleton


class DbManager(Singleton):
    def __init__(self):
        settings = get_project_settings()
        ibm_db_dbi.threadsafety=1
        connKwargs = {'dsn':'DATABASE='+settings['DB2_DBNAME']+';HOSTNAME='+settings['DB2_HOST']+';UID='+settings['DB2_USER']+';PWD='+settings['DB2_PASSWORD']+';PORT='+str(settings['DB2_PORT']),
                      # 'conn_options':{'SQL_ATTR_AUTOCOMMIT': ibm_db.SQL_AUTOCOMMIT_ON}
                      }
        self._pool = PooledDB(ibm_db_dbi, mincached=0, maxcached=10, maxshared=10, maxusage=10000, **connKwargs)
    def getConn(self):
        return self._pool.connection()

_dbManager = DbManager()

def getConn():
    """ 获取数据库连接 """
    return _dbManager.getConn()

def executeAndGetId(sql, param=None):
    """ 执行插入语句并获取自增id """
    conn = getConn()
    conn.set_autocommit(True)
    cursor = conn.cursor()
    if param == None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, param)
    id = cursor.lastrowid
    cursor.close()
    conn.close()
    return id

def execute(sql, param=None):
    """ 执行sql语句 """
    conn = getConn()
    cursor = conn.cursor()
    rowcount = cursor.execute(sql, param)
    # if param == None:
    #     rowcount = cursor.execute(sql)
    # else:
    #     rowcount = cursor.execute(sql, param)
    cursor.close()
    conn.close()
    return rowcount

def queryOne(sql):
    """ 获取一条信息 """
    conn = getConn()
    cursor = conn.cursor()
    rowcount = cursor.execute(sql)
    if rowcount > 0:
        res = cursor.fetchone()
    else:
        res = None
    cursor.close()
    conn.close()
    return res

def queryAll(sql):
    """ 获取所有信息 """
    conn = getConn()
    cursor = conn.cursor()
    rowcount = cursor.execute(sql)
    if rowcount > 0:
        res = cursor.fetchall()
    else:
        res = None
    cursor.close()
    conn.close()
    return res

def insertOne(sql, value):
    conn = getConn()
    cursor = conn.cursor()
    rowcount = cursor.execute(sql, value)
    conn.commit()
    cursor.close()
    conn.close()
    return rowcount

def insertMany(sql, values):
    conn = getConn()
    cursor = conn.cursor()
    rowcount = cursor.executemany(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
    return rowcount

# if __name__ == "__main__":
#     res = queryAll('select name from CREDITCHINA.QUERY_CUST_LIST order BY sid ASC ')
#     l=[]
#     for r in list(res):
#         l.append(r[0])
#     print l
