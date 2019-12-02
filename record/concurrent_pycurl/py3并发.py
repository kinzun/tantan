# !/usr/bin/python
# -*- coding: utf-8 -*-
import time
from io import StringIO, BytesIO
from collections import namedtuple
from pprint import pprint
import pycurl


def muti_curl():
    # 最大连接数
    num_conn = 20

    queue = []
    # urls = ['http://www.baidu.com/'] * 10
    urls = ['http://127.0.0.1:8082/'] * 10
    for url in urls:
        queue.append(url)

    num_urls = len(queue)
    num_conn = min(num_conn, num_urls)
    print('----- Getting', num_urls, 'Max conn', num_conn,
          'connections -----')

    m = pycurl.CurlMulti()
    # 初始化handle，可复用
    m.handles = []
    for i in range(num_conn):
        c = pycurl.Curl()
        # c.body = StringIO()
        c.body = BytesIO()
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.CONNECTTIMEOUT, 30)
        c.setopt(pycurl.TIMEOUT, 300)
        c.setopt(pycurl.NOSIGNAL, 1)
        m.handles.append(c)

    freelist = m.handles[:]
    num_processed = 0
    # 主循环开始

    while num_processed < num_urls:

        # 添加请求URL
        while queue and freelist:
            url = queue.pop()
            c = freelist.pop()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.WRITEFUNCTION, c.body.write)
            m.add_handle(c)
            c.url = url
            # print url

        # 执行请求
        while 1:
            (ret, num_handles) = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break

        # 阻塞一会直到有连接完成
        m.select(1.0)

        # 读取完成的连接
        while 1:
            (num_q, ok_list, err_list) = m.info_read()
            for c in ok_list:
                m.remove_handle(c)
                # print c.body.getvalue()
                freelist.append(c)

            for (c, errno, errmsg) in err_list:
                m.remove_handle(c)
                print('Failed: ', c.url, errno, errmsg)
                freelist.append(c)
            num_processed = num_processed + len(ok_list) + len(err_list)
            if num_q == 0:
                break

    for c in m.handles:
        c.fp = None
        c.close()
    m.close()
