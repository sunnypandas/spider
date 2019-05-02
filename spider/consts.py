MYSQL_ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
    'spider.pipelines.MySqlPipeline': 100,
}

DB2_ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
    'spider.pipelines.DB2Pipeline': 100,
}

DOWNLOADER_MIDDLEWARES_HTTP_PROXY_ON = {
    #'spider.middlewares.DownloaderMiddleware': 543,
    #to support random ua
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    #to support proxy
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy_proxies.RandomProxy': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

DOWNLOADER_MIDDLEWARES_HTTP_PROXY_OFF = {
    #'spider.middlewares.DownloaderMiddleware': 543,
    #to support random ua
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    #to support splash
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

DOWNLOADER_MIDDLEWARES_TOR_PROXY_ON = {
    #'spider.middlewares.DownloaderMiddleware': 543,
    #to support random ua
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    #to support proxy
    'spider.middlewares.TorProxyMiddleware': 543,
}

DOWNLOADER_MIDDLEWARES_TOR_PROXY_OFF = {
    #'spider.middlewares.DownloaderMiddleware': 543,
    #to support random ua
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}

DOWNLOADER_MIDDLEWARES_SQUID_PROXY_ON = {
    #'spider.middlewares.DownloaderMiddleware': 543,
    #to support random ua
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    #to support proxy
    'spider.middlewares.SquidProxyMiddleware': 543,
}

DOWNLOADER_MIDDLEWARES_SQUID_PROXY_OFF = {
    #'spider.middlewares.DownloaderMiddleware': 543,
    #to support random ua
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}