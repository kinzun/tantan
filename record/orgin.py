# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
from io import StringIO, BytesIO
from collections import namedtuple
from pprint import pprint
import pycurl


class multithreading():
    num_conn_pool = 10

    def __init__(self, urls):
        self.urls = urls

    def pool_crete(self):
        curlmulti_obj = pycurl.CurlMulti()
        # 初始化handle，可复用
        curlmulti_obj.handles = []
        # for i in range(self.num_conn_pool):
        for i in range(len(urls)):
            c = pycurl.Curl()
            # c.body = StringIO()
            c.body = BytesIO()
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.CONNECTTIMEOUT, 30)
            c.setopt(pycurl.TIMEOUT, 300)
            c.setopt(pycurl.NOSIGNAL, 1)
            curlmulti_obj.handles.append(c)

        return curlmulti_obj

    def excute(self):
        # 执行请求
        curlmulti_obj = self.pool_crete()
        freelist = curlmulti_obj.handles[:]
        num_processed = 0
        num_urls = len(self.urls)

        "状态码 连接时间 接收到第一个字节的时间 总时间"
        monitor = namedtuple("Monitor",
                             ["URL", "body", "http_code", "connect_time", "starttransfer_time", "total_time"])

        all_url_info = []

        while num_processed < num_urls:

            # 添加请求URL
            while urls and freelist:
                url = urls.pop()
                c = freelist.pop()
                c.setopt(pycurl.URL, url)
                c.setopt(pycurl.WRITEFUNCTION, c.body.write)
                curlmulti_obj.add_handle(c)
                c.url = url
                print(url)

            # 执行请求
            while 1:
                (ret, num_handles) = curlmulti_obj.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break

            # 阻塞一会直到有连接完成
            curlmulti_obj.select(1.0)

            # 读取完成的连接

            while 1:
                (num_q, ok_list, err_list) = curlmulti_obj.info_read()
                for c in ok_list:
                    curlmulti_obj.remove_handle(c)
                    body = c.body.getvalue()
                    http_code = c.getinfo(pycurl.HTTP_CODE)
                    http_conn_time = c.getinfo(pycurl.CONNECT_TIME)
                    http_pre_tran = c.getinfo(pycurl.PRETRANSFER_TIME)
                    http_total_time = c.getinfo(pycurl.TOTAL_TIME)
                    http_start_tran = c.getinfo(pycurl.STARTTRANSFER_TIME)
                    # print(http_code, http_conn_time, http_pre_tran)
                    # print(c.getinfo_raw(pycurl.EFFECTIVE_URL))
                    all_url_info.append(
                        monitor(c.url, body, http_code, http_conn_time, http_start_tran, http_total_time))
                    # all_url_dict[url] = monitor(c.url, http_code, http_conn_time, http_start_tran, http_total_time)
                    freelist.append(c)

                for (c, errno, errmsg) in err_list:
                    curlmulti_obj.remove_handle(c)
                    print('Failed: ', c.url, errno, errmsg)
                    freelist.append(c)
                num_processed = num_processed + len(ok_list) + len(err_list)
                if num_q == 0:
                    break

        return all_url_info

    def url_list(self, urls):
        urls = [i for i in urls]


urls = ["http://www.baojia.com/"] * 10
# urls = ['http://127.0.0.1:8082/curl/'] * 100
# urls = ['http://www.baidu.com/'] * 50
# urls = ['http://127.0.0.1:8888/'] * 100
# urls = ['www.guazi.com', 'http://www.jrj.com.cn/', 'https://www.pconline.com.cn/?ad=6348', 'http://mobile.zol.com.cn/',
#         'https://www.sogou.com/']

start = time.time()
curl = multithreading(urls)
s = curl.excute()
# pprint(s)
# print(len(s))
print(time.time() - start)
