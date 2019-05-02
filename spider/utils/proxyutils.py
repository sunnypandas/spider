# -*- coding: UTF-8 -*-
import logging
import os
import socket
import urllib
from configparser import ConfigParser
from json import load
from multiprocessing.pool import Pool
from urllib.request import urlopen
import requests
import ssl
from sklearn.externals.joblib._multiprocessing_helpers import mp
from spider.utils.mysqlutils import Mysql

def is_bad_proxy(site,pip,domain,proxy,ip,port,anonymous_status):
    try:
        proxy_handler = urllib.request.ProxyHandler(pip)
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        req=urllib.request.Request(site)
        sock=urlopen(req,timeout=5)
    except urllib.request.HTTPError as e:
        # logging.error( 'Error code: %s', e.code)
        return True,domain,proxy,ip,port,anonymous_status
    except Exception as detail:
        # logging.error("ERROR: %s", detail)
        return True,domain,proxy,ip,port,anonymous_status
    return False,domain,proxy,ip,port,anonymous_status

def write_available_result(result):
    if result[0]==True:
        pass
        # logging.error("Bad Proxy %s", result[1])
    else:
        # logging.warning("%s is working", result)
        Mysql().insertOne("INSERT INTO proxy_list_domain (WEB_DOMAIN, PROXY, PROXY_URL, ANONYMOUS_STATUS) VALUES (%s, %s, %s, %s)",[result[1],result[2],result[2]+'://'.encode('UTF-8')+result[3]+':'.encode('UTF-8')+result[4],result[5]])
        # file = open('proxy.txt', 'a')
        # file.write(result[1] + '\n')

def available_testing(domain):
    # logging.warning("Empty result file")
    # open('proxy.txt', 'w+')
    socket.setdefaulttimeout(5)
    pool = mp.Pool(processes=32)
    config = ConfigParser()
    # domain='www.ali213.net'
    config.read(os.path.abspath(os.path.dirname(__file__))+'/config.ini')
    website = config.get(domain, 'website')
    webproxy = config.get(domain, 'webproxy')
    webdomain = config.get(domain, 'webdomain')
    proxyList = Mysql().getAll("SELECT * FROM proxy_list_all" , [])
    for currentProxy in proxyList:
        pool.apply_async(is_bad_proxy, args = (website,{currentProxy['PROXY'].lower(): currentProxy['IP']+':'.encode('UTF-8')+currentProxy['PORT']},webdomain,currentProxy['PROXY'].lower(),currentProxy['IP'],currentProxy['PORT'],currentProxy['ANONYMOUS_STATUS'] ), callback = write_available_result)
    pool.close()
    pool.join()

def is_anonymous_proxy(proxy,ip,port,myIp):
    s = requests.Session()
    s.proxies.update({proxy: ip + ':' + port})
    try:
        response = s.get('http://httpbin.org/ip',timeout=5)
        if response.status_code==200:
            #logging.warning("%s is working",proxy + '://' + ip + ':' + port)
            if myIp in response.text:
                return 'transparent',proxy,ip,port
            else:
                return 'anonymous',proxy,ip,port
        else:
            'error', proxy, ip, port
    except:
        # logging.warning("%s is error",proxy + '://' + ip + ':' + port)
        return 'error',proxy,ip,port

def write_anonymous_result(result):
    try:
        Mysql().update("UPDATE proxy_list_all SET ANONYMOUS_STATUS = %s WHERE PROXY = %s AND IP = %s AND PORT = %s ",result)
    except:
        logging.error("insert table error: %s", result)
def anonymous_testing():
    myIp = load(urlopen('http://httpbin.org/ip'))['origin']
    socket.setdefaulttimeout(5)
    pool = mp.Pool(processes=32)
    proxyList = Mysql().getAll("SELECT * FROM proxy_list_all")
    for currentProxy in proxyList:
        pool.apply_async(is_anonymous_proxy, args=(currentProxy['PROXY'].lower(),currentProxy['IP'],currentProxy['PORT'],myIp),callback=write_anonymous_result)
    pool.close()
    pool.join()

def createProxyFile(domain=None,proxy=None,anonymous=None):
    proxyList=[]
    if domain!=None and proxy!=None and anonymous!=None:
        proxyList = Mysql().getAll("SELECT * FROM proxy_list_domain WHERE WEB_DOMAIN = %s AND PROXY = %s AND ANONYMOUS_STATUS = %s",[domain, proxy, anonymous])
    else:
        if domain != None and proxy != None and anonymous == None:
            proxyList = Mysql().getAll("SELECT * FROM proxy_list_domain WHERE WEB_DOMAIN = %s AND PROXY = %s",[domain, proxy])
        else:
            if domain != None and proxy == None and anonymous != None:
                proxyList = Mysql().getAll("SELECT * FROM proxy_list_domain WHERE WEB_DOMAIN = %s AND ANONYMOUS_STATUS = %s",[domain, anonymous])
            else:
                if domain != None and proxy == None and anonymous == None:
                    proxyList = Mysql().getAll("SELECT * FROM proxy_list_domain WHERE WEB_DOMAIN = %s", [domain])
                else:
                    logging.warning('domain cannot be empty!')
                    return
    file = open('proxy.txt', 'w+')
    for currentProxy in proxyList:
        file.write(currentProxy['PROXY_URL'] + '\n')

GOOD_PROXIES = []

def check_proxy(proxy):
    global GOOD_PROXIES
    ip, port = proxy
    _proxies = {
        'http': '{}:{}'.format(ip, port)
    }
    try:
        res = requests.get(
            'http://1212.ip138.com/ic.asp', proxies=_proxies, timeout=10)
        assert ip in res.content
        logging.info('[GOOD] - {}:{}'.format(ip, port))
        GOOD_PROXIES.append(proxy)
    except Exception as e:
        logging.error('[BAD] - {}:{}, {}'.format(ip, port, e))

def update_conf():
    PEER_CONF = "cache_peer %s parent %s 0 no-query weighted-round-robin weight=1 connect-fail-limit=2 allow-miss max-conn=5\n"
    with open('/etc/squid/squid.conf.original', 'r') as F:
        squid_conf = F.readlines()
    squid_conf.append('\n# Cache peer config\n')
    for proxy in GOOD_PROXIES:
        squid_conf.append(PEER_CONF % (proxy[0], proxy[1]))
    with open('/etc/squid/squid.conf', 'w') as F:
        F.writelines(squid_conf)

def get_proxy_api():
    pool = Pool(50)
    api_url = 'http://s.zdaye.com/?api=YOUR_API&count=100&fitter=1&px=2'
    res = requests.get(api_url).content
    if len(res) == 0:
        logging.error('no data')
    elif 'bad' in res:
        logging.error('bad request')
    else:
        logging.info('get all proxies')
        proxies = []
        for line in res.split():
            proxies.append(line.strip().split(':'))
        pool.map(check_proxy, proxies)
        pool.join()
        update_conf()
        os.system('squid -k reconfigure')
        logging.info('>>>> DONE! <<<<')
def get_proxy_local():
    PEER_CONF = "cache_peer %s parent %s 0 no-query weighted-round-robin weight=1 connect-fail-limit=2 allow-miss max-conn=5"
    proxyList = Mysql().getAll("SELECT * FROM proxy_list_all",[])
    proxies = []
    for proxy in proxyList:
        print(PEER_CONF % (proxy['IP'].decode('UTF-8'), proxy['PORT'].decode('UTF-8')))
def get_squid_api():
    http_proxy_server = "47.105.51.111"
    http_proxy_port = "4238"
    http_proxy_user = "squid"
    http_proxy_passwd = "squid2018"

    http_proxy_full_auth_string = "https://%s:%s@%s:%s" % (http_proxy_user,
                                                          http_proxy_passwd,
                                                          http_proxy_server,
                                                          http_proxy_port)
    proxy_handler = urllib.request.ProxyHandler({"https": http_proxy_full_auth_string})

    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)
    context = ssl._create_unverified_context()
    response = urllib.request.urlopen('https://www.creditchina.gov.cn', context = context)
    html_response = response.read()
    encoding = response.headers.get_content_charset('utf-8')
    decoded_html = html_response.decode(encoding)
    print(decoded_html)

def main():
    # available_testing('www.ali213.net')
    get_squid_api()
    # start = time.time()
    # while True:
    #     if time.time() - start >= 30:
    #         get_proxy_api()
    #         start = time.time()
    #     time.sleep(5)


if __name__ == '__main__':
    main()