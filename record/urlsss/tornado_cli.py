import json
import sys
import os
import time
from io import BytesIO
from collections import namedtuple
import pycurl
import asyncio
from tornado.httpclient import AsyncHTTPClient
from tornado import ioloop
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPClientError
from urlsss.new_curl_tornado import CurlError
from urlsss.read_xlsx import ret_urls
from pprint import pprint

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

from tornado.curl_httpclient import CurlAsyncHTTPClient

from requests.models import Response
import chardet


class Response(object):
    "处理 流响应内容"

    def __init__(self, content):
        """"""
        self._content = content
        self.encoding = None

    @property
    def apparent_encoding(self):
        """The apparent encoding, provided by the chardet library."""
        return chardet.detect(self.content)['encoding']

    @property
    def content(self):
        if self._content is False:
            self._content = b''.join(self._content or b'')

        return self._content

    @property
    def text(self):
        content = None
        encoding = self.encoding

        if not self.content:
            return str('')

        if self.encoding is None:
            encoding = self.apparent_encoding

        try:
            content = str(self.content, encoding, errors='replace')
        except (LookupError, TypeError):
            content = str(self.content, errors='replace')

        return content

    @staticmethod
    def binary_to_html(binary):
        text = binary.decode('utf-8')
        return text


class Post_curl(object):

    def post(self):
        pass


class tornado_curl(object):

    @staticmethod
    async def fetch_async(url_tuple):
        AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=30)
        # AsyncHTTPClient.configure("urlsss.new_curl_tornado.CurlAsyncHTTPClient", max_clients=30)
        http_client = AsyncHTTPClient()

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
                response = await http_client.fetch(url_tuple.url[0], connect_timeout=20, request_timeout=20)


        # except Exception as e:
        except HTTPClientError as e:
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
                DICT_INFO[url_tuple.url[0]] = response.time_info
            else:

                # DICT_INFO.append(response)
                DICT_INFO[url_tuple.url[0]] = response

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

        s = url_info(name='baojia', url=['http://wangguan.baojia.com/appQuery/btMac'],
                     return_msg=['No message available'], code=[404],
                     real_host=['47.94.14.14', '47.94.147.183'])

        tasks = []
        for i in all_urls:
            tasks.append(tornado_curl.fetch_async(i))
            # break
        # tasks.append(tornado_curl.fetch_async(s))

        start = time.time()
        event_loop = asyncio.get_event_loop()
        results = event_loop.run_until_complete(asyncio.gather(*tasks))
        event_loop.close()
        pprint(DICT_INFO)
        print(time.time() - start)


#
#
tornado_curl.run()

with open('url_time_info.json', mode='w', ) as f:
    json.dump(DICT_INFO, f, sort_keys=True, indent=4)

# all_urls = ret_urls()
# pprint(all_urls)
# print(len(all_urls))
