import re
from urllib.parse import unquote_plus, quote_plus
import json
import sys
import os
from collections import namedtuple
import time
import asyncio
from tornado.httpclient import AsyncHTTPClient
# from tornado import ioloop
# from tornado.ioloop import IOLoop

from tornado.httpclient import HTTPClientError
# from bin.new_curl_tornado import CurlError
from bin.read_xlsx import ret_urls
from bin.response import Response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_DIR)

DICT_INFO = {}


# 默认client是基于ioloop实现的，配置使用Pycurl
# AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=20)
# http_client = AsyncHTTPClient()
# for i in range(count):
#     http_client.fetch("http://127.0.0.1:8082", handle_request)


# 死循环
# IOLoop.instance().start()

# from tornado.curl_httpclient import CurlAsyncHTTPClient


class Post_curl(object):

    def post(self):
        pass


def func():
    pass


def url_conversion(url, item_name):
    regular = re.compile("(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]")
    if regular.search(item_name):
        re_item_url = regular.findall(item_name)
        if unquote_plus(re_item_url[0]) == unquote_plus(url):
            return True
    else:
        return item_name


class tornado_curl(object):

    @staticmethod
    def response_content(url_info, response_):
        """响应类型 和响应内容的判断..."""
        try:
            content_type = response_.headers.get('Content-Type')
            if "json" in content_type:
                Response(response_.body).json()
                return response_
            else:
                content = Response(response_.body).text
                if url_info.return_msg in content:
                    return response_
                else:
                    return response_
                return response_

        except Exception as e:
            print(e)
            pass
            # print(e)
            # return response_

    @staticmethod
    async def real_fetch_async(http_client, res_urls):

        real_dict = {}

        for url_get in res_urls:
            try:
                real_response = await http_client.fetch(url_get, connect_timeout=5, request_timeout=5)
            except Exception as e:
                real_response = {"url": url_get, "code": e.code, "message": e.message, "total": ''}

                if 200 <= e.code < 500:
                    real_response.update(e.response.time_info)
            finally:
                if hasattr(real_response, "time_info"):
                    real_response.time_info['url'] = url_get
                    real_response.time_info['code'] = real_response.code
                    real_dict[quote_plus(url_get)] = real_response.time_info
                else:
                    real_dict[quote_plus(url_get)] = real_response

        return real_dict

    @staticmethod
    async def try_three(http_client, url_tuple):
        i = 0
        response = ""
        while i < 2:
            try:
                response = await  http_client.fetch(url_tuple.url[0], connect_timeout=10,
                                                    request_timeout=10)

                return tornado_curl.response_content(url_tuple, response)
            except HTTPClientError as e:
                i += 1
                response = {"url": url_tuple.url[0], "code": e.code, "message": e.message,
                            "total": e.response.time_info.get("total")
                            }

                if 200 <= e.code < 500:
                    response.update(e.response.time_info)
        return response

    @staticmethod
    async def fetch_async(url_tuple):
        # AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=30)
        AsyncHTTPClient.configure("bin.new_curl_tornado.CurlAsyncHTTPClient", max_clients=30)
        http_client = AsyncHTTPClient()
        response = ""

        # "状态码 连接时间 接收到第一个字节的时间 总时间"
        # monitor = namedtuple("Monitor",
        #                      ["URL", "body", "http_code", "connect_time", "starttransfer_time", "total_time"])

        try:
            if url_tuple.url[0] == "http://wangguan.baojia.com/appQuery/btMac":
                # https://github.com/tornadoweb/tornado/blob/master/demos/file_upload/file_uploader.py
                headers = {"Content-Type": "application/json"}
                response = await http_client.fetch(url_tuple.url[0],
                                                   method="POST",
                                                   headers=headers,
                                                   body=json.dumps({"frm": "tmp", "carId": "864376046631916"}),
                                                   connect_timeout=20, request_timeout=20)

            else:

                # 如果报错，重试3次.
                response = await tornado_curl.try_three(http_client, url_tuple)

                if url_tuple.real_host:
                    readl = await  tornado_curl.real_fetch_async(http_client=http_client,
                                                                 res_urls=url_tuple.real_host,
                                                                 )
                    response.time_info['backend_real'] = readl



        # except Exception as e:
        except HTTPClientError as e:
            # print("Error: %s" % e.response)
            # print("Error: %s" % e.response.time_info)

            response = {"url": url_tuple.url[0], "code": e.code, "message": e.message, "total": ''}
            if 200 <= e.code < 500:
                response.update(e.response.time_info)
            # print(response)
            # print(e.response.time_info)
            # print(response)

        else:
            pass
            # print(response.headers)
            # print(response.request_time)
            # print(response.start_time)
            # print(response.elapsed.total_seconds())
            # print(response.effective_url)
            # print(response.code)
            # print(response.time_info)
            # print(response.reason)
            # print(response.body)
        finally:
            if hasattr(response, "time_info"):
                response.time_info['url'] = url_tuple.url[0]
                response.time_info['code'] = response.code
                # response.time_info['body'] = Response(response.body).text
                # DICT_INFO.append(response.time_info)
                DICT_INFO[quote_plus(url_tuple.url[0])] = response.time_info
                return response.time_info
            else:
                # DICT_INFO.append(response)
                DICT_INFO[quote_plus(url_tuple.url[0])] = response
                return response

        """
            namelookup_time: 解析时间， 从开始直到解析完远程请求的时间；
            connect_time: 建立连接时间,从开始直到与远程请求服务器建立连接的时间；
            pretransfer_time: 从开始直到第一个远程请求接收到第一个字节的时间；
            starttranster_time: 从开始直到第一个字节返回给curl的时间；(响应时间)
            服务器数据响应时间:  starttransfer_time - pretransfer_time 得到请求 服务器处理的时间。
            total_time： 从开始直到结束的所有时间。
        """

        # tasks = [fetch_async('http://www.google.com/'), fetch_async('http://www.cnblogs.com/ssyfj/'),

        #          fetch_async('http://baojia.com')]

        # tasks = [fetch_async("http://127.0.0.1:8082/curl/")] * 50
        # tasks = [fetch_async("http://127.0.0.1:8082/curl/") for i in range(50)]

        # io_loop = ioloop.IOLoop.current()
        # io_loop.run_sync()

    @staticmethod
    def run():
        all_urls = ret_urls()

        url_info = namedtuple('urls_info', ['name', 'url', 'return_msg', 'code', 'real_host'])

        # s = url_info(name='baojia', url=['http://wangguan.baojia.com/appQuery/btMac'],
        #              return_msg=['No message available'], code=[404],
        #              real_host=['47.94.14.14', '47.94.147.183'])
        #
        """ 测试用url """
        # s = url_info(name='bike-bike', url=['https://me.baojia.com/'], return_msg=['没有相关操作权限'], code=[200],
        #              real_host=[])
        # se = url_info(name='换电柜网关系统io、cloud', url=['211.151.2.246:38026'], return_msg=['1341'], code=[200],
        #               real_host=[])
        # se1 = url_info(name='pmall线上', url=['http://me.baojia.com/pmall/allProduct'], return_msg=['操作成功'], code=[200],
        #                real_host=[])
        # se2 = url_info(name='web前端 计价规则', url=['http://static.meboth.cn/xiaomi/metripapp/20180913/rule.html'],
        #                return_msg=['计价规则'], code=[200],
        #                real_host=[])
        #
        # tasks = []
        # tasks.append(tornado_curl.fetch_async(s))
        # tasks.append(tornado_curl.fetch_async(se))
        # tasks.append(tornado_curl.fetch_async(se1))
        # tasks.append(tornado_curl.fetch_async(se2))

        tasks = []
        for i in all_urls:
            tasks.append(tornado_curl.fetch_async(i))

        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(asyncio.gather(*tasks))
        event_loop.close()

        with open(os.path.join(BASE_DIR, 'url_time_info.json'), mode='w', ) as f:
            json.dump(DICT_INFO, f, sort_keys=True, indent=4)


def file_time_diff():
    return time.time() - os.path.getctime(os.path.join(BASE_DIR), 'url_time_info') >= 30



if __name__ == '__main__':
    tornado_curl.run()

    # import cProfile
    #
    # cProfile.run("tornado_curl.run()", "prof.txt")
    # import pstats
    #
    # p = pstats.Stats("prof.txt")
    # p.sort_stats("time").print_stats()
