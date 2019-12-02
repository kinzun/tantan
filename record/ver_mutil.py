import pycurl
import time
from collections import namedtuple
from typing import Dict, Any, Callable, Union
from pprint import pprint
from io import BytesIO

import collections


class multithreading(object):
    num_conn_pool = 10
    monitor = namedtuple("Monitor", ["URL", "http_code", "connect_time", "starttransfer_time", "total_time"])

    def __new__(cls, *args, **kwargs):
        instance = super(multithreading, cls).__new__(cls)
        instance.initialize()
        cls.urls = urls
        return instance

    # def __init__(self, urls):
    #     self.urls = urls
    #     self.DEBUG = False

    def initialize(  # type: ignore
            self, max_clients: int = 10, defaults: Dict[str, Any] = None
    ) -> None:
        self._multi = pycurl.CurlMulti()
        self._multi.handles = []
        self._curls = [self._curl_create() for i in range(max_clients)]

        [self._multi.handles.append(i) for i in self._curls]

        self._free_list = self._curls[:]
        self._requests = (
            collections.deque()
        )

    #     popleft

    def perform(self):
        free_list = self._multi.handles[:]
        num_processed = 0
        num_urls = len(self.urls)
        all_url_info = []

        "状态码 连接时间 接收到第一个字节的时间 总时间"
        monitor = namedtuple("Monitor", ["URL", "http_code", "connect_time", "starttransfer_time", "total_time"])
        while num_processed < num_urls:

            # 添加请求URL
            while urls and free_list:
                url = urls.pop()
                c = free_list.pop()
                c.body = BytesIO()
                c.setopt(pycurl.URL, url)
                c.setopt(pycurl.WRITEFUNCTION, c.body.write)
                self._multi.add_handle(c)
                c.url = url

            # 执行请求
            while 1:
                (ret, num_handles) = self._multi.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break

            # 阻塞一会直到有连接完成
            self._multi.select(1.0)

            # 读取完成的连接

            while 1:
                (num_q, ok_list, err_list) = self._multi.info_read()
                for curl in ok_list:
                    self._multi.remove_handle(curl)
                    self._finish(curl)
                    print(c.body.getvalue())

                    all_url_info.append(self.finish(curl))

                    # all_url_info.append(monitor(c.url, http_code, http_conn_time, http_start_tran, http_total_time))
                    free_list.append(c)

                for (c, errno, errmsg) in err_list:
                    self._multi.remove_handle(c)
                    print('Failed: ', c.url, errno, errmsg)
                    free_list.append(c)
                num_processed = num_processed + len(ok_list) + len(err_list)
                if num_q == 0:
                    break

    def finish(self, curl: pycurl.Curl):
        http_code = curl.getinfo(pycurl.HTTP_CODE)
        http_conn_time = curl.getinfo(pycurl.CONNECT_TIME)
        http_pre_tran = curl.getinfo(pycurl.PRETRANSFER_TIME)
        http_total_time = curl.getinfo(pycurl.TOTAL_TIME)
        http_start_tran = curl.getinfo(pycurl.STARTTRANSFER_TIME)
        print(http_code, http_conn_time, http_pre_tran)
        print(curl.getinfo_raw(pycurl.EFFECTIVE_URL))
        return self.monitor(curl.getinfo(pycurl.EFFECTIVE_URL), http_code, http_conn_time, http_start_tran,
                            http_total_time)

    def _curl_create(self, DEBUG=None) -> pycurl.Curl:

        curl = pycurl.Curl()
        if DEBUG:
            curl.setopt(pycurl.VERBOSE, 1)
            curl.setopt(pycurl.DEBUGFUNCTION, self._curl_debug)
        if hasattr(
                pycurl, "PROTOCOLS"
        ):  # PROTOCOLS first appeared in pycurl 7.19.5 (2014-07-12)
            curl.setopt(pycurl.PROTOCOLS, pycurl.PROTO_HTTP | pycurl.PROTO_HTTPS)
            curl.setopt(pycurl.REDIR_PROTOCOLS, pycurl.PROTO_HTTP | pycurl.PROTO_HTTPS)
            curl.setopt(pycurl.TIMEOUT, 10)
            curl.setopt(pycurl.CONNECTTIMEOUT, 30)

        return curl

    def _process_queue(self) -> None:
        while True:
            started = 0
            while self._free_list and self._requests:
                started += 1
                curl = self._free_list.pop()
                (request, callback, queue_start_time) = self._requests.popleft()
                curl.info = {
                    # "headers": httputil.HTTPHeaders(),
                    "buffer": BytesIO(),
                    "request": request,
                    "callback": callback,
                    "queue_start_time": queue_start_time,
                    "curl_start_time": time.time(),
                    "curl_start_ioloop_time": self.io_loop.current().time(),
                }
                try:
                    self._curl_setup_request(
                        curl, request, curl.info["buffer"], curl.info["headers"]
                    )
                except Exception as e:
                    # If there was an error in setup, pass it on
                    # to the callback. Note that allowing the
                    # error to escape here will appear to work
                    # most of the time since we are still in the
                    # caller's original stack frame, but when
                    # _process_queue() is called from
                    # _finish_pending_requests the exceptions have
                    # nowhere to go.
                    self._free_list.append(curl)
                else:
                    self._multi.add_handle(curl)

            if not started:
                break

    def _finish_pending_requests(self) -> None:
        """Process any requests that were completed by the last
        call to multi.socket_action.
        """
        while True:
            num_q, ok_list, err_list = self._multi.info_read()
            for curl in ok_list:
                self._finish(curl)
            for curl, errnum, errmsg in err_list:
                self._finish(curl, errnum, errmsg)
            if num_q == 0:
                break
        self._process_queue()

    def _finish(self, curl: pycurl.Curl, curl_error: int = None, curl_message: str = None) -> None:
        info = curl.info
        curl.info = None
        self._multi.remove_handle(curl)
        self._free_list.append(curl)
        buffer = info["buffer"]
        if curl_error:
            effective_url = None
            buffer.close()
            buffer = None
        else:
            error = None
            code = curl.getinfo(pycurl.HTTP_CODE)
            effective_url = curl.getinfo(pycurl.EFFECTIVE_URL)
            buffer.seek(0)
        # the various curl timings are documented at
        # http://curl.haxx.se/libcurl/c/curl_easy_getinfo.html
        time_info = dict(
            queue=info["curl_start_ioloop_time"] - info["queue_start_time"],
            namelookup=curl.getinfo(pycurl.NAMELOOKUP_TIME),
            connect=curl.getinfo(pycurl.CONNECT_TIME),
            appconnect=curl.getinfo(pycurl.APPCONNECT_TIME),
            pretransfer=curl.getinfo(pycurl.PRETRANSFER_TIME),
            starttransfer=curl.getinfo(pycurl.STARTTRANSFER_TIME),
            total=curl.getinfo(pycurl.TOTAL_TIME),
            redirect=curl.getinfo(pycurl.REDIRECT_TIME),
        )
        # try:
        #     info["callback"](
        #         request=info["request"],
        #         code=code,
        #         headers=info["headers"],
        #         buffer=buffer,
        #         effective_url=effective_url,
        #         error=error,
        #         reason=info["headers"].get("X-Http-Reason", None),
        #         request_time=self.io_loop.time() - info["curl_start_ioloop_time"],
        #         start_time=info["curl_start_time"],
        #         time_info=time_info,
        # )

    # def _curl_setup_request(self)

    def pool_crete(self):
        self._multi = pycurl.CurlMulti()
        # 初始化handle，可复用
        self._multi.handles = []
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
            self._multi.handles.append(c)
        return self._multi

    def excute(self):
        # 执行请求
        self._multi = self.pool_crete()
        freelist = self._multi.handles[:]
        num_processed = 0
        num_urls = len(self.urls)

        "状态码 连接时间 接收到第一个字节的时间 总时间"
        monitor = namedtuple("Monitor", ["URL", "http_code", "connect_time", "starttransfer_time", "total_time"])

        all_url_info = []

        while num_processed < num_urls:

            # 添加请求URL
            while urls and freelist:
                url = urls.pop()
                c = freelist.pop()
                c.setopt(pycurl.URL, url)
                c.setopt(pycurl.WRITEFUNCTION, c.body.write)
                self._multi.add_handle(c)
                c.url = url
                print(url)

            # 执行请求
            while 1:
                (ret, num_handles) = self._multi.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break

            # 阻塞一会直到有连接完成
            self._multi.select(1.0)

            # 读取完成的连接

            while 1:
                (num_q, ok_list, err_list) = self._multi.info_read()
                for c in ok_list:
                    self._multi.remove_handle(c)
                    # print(c.body.getvalue())
                    http_code = c.getinfo(pycurl.HTTP_CODE)
                    http_conn_time = c.getinfo(pycurl.CONNECT_TIME)
                    http_pre_tran = c.getinfo(pycurl.PRETRANSFER_TIME)
                    http_total_time = c.getinfo(pycurl.TOTAL_TIME)
                    http_start_tran = c.getinfo(pycurl.STARTTRANSFER_TIME)
                    # print(http_code, http_conn_time, http_pre_tran)
                    http_url = c.getinfo(pycurl.EFFECTIVE_URL)
                    all_url_info.append(monitor(http_url, http_code, http_conn_time, http_start_tran, http_total_time))

                    # all_url_dict[url] = monitor(c.url, http_code, http_conn_time, http_start_tran, http_total_time)
                    freelist.append(c)

                for (c, errno, errmsg) in err_list:
                    self._multi.remove_handle(c)
                    print('Failed: ', c.url, errno, errmsg)
                    freelist.append(c)
                num_processed = num_processed + len(ok_list) + len(err_list)
                if num_q == 0:
                    break

        return all_url_info

    def url_list(self, urls):
        urls = [i for i in urls]


# urls = ['http://127.0.0.1:8082/curl/1'] * 10
urls = ['http://127.0.0.1:8082/curl/'] * 100
# urls = ['http://127.0.0.1:8082/'] * 100


# urls = ['www.guazi.com', 'http://www.jrj.com.cn/', 'https://www.pconline.com.cn/?ad=6348', 'http://mobile.zol.com.cn/',
#         'https://www.sogou.com/']

start = time.time()

curl = multithreading(urls=urls)
# curl._curl_create()
s = curl.excute()
# pprint(s)
# print(len(s))
# print(time.time() - start)
