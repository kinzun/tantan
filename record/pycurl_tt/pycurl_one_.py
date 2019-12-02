import pycurl

from collections import namedtuple


class Pycurl_cu(object):
    # num_conn_pool = 10
    # monitor = namedtuple("Monitor", ["URL", "http_code", "connect_time", "starttransfer_time", "total_time"])

    def __new__(cls, *args, **kwargs):
        instance = super(Pycurl_cu, cls).__new__(cls)
        instance.initialize()
        cls.url = url
        return instance

    # def __init__(self, urls):
    #     self.url = urls
    #     self.DEBUG = False

    def initialize(  # type: ignore
            self, max_clients: int = 10
    ) -> None:

        self.curl = self._curl_create()
        self.buffer = BytesIO()
        self.curl.setopt(self.curl.URL, self.url)
        self.curl.setopt(self.curl.WRITEDATA, self.buffer)
        self.curl.perform()

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
            curl.setopt(pycurl.MAXREDIRS, 5)
            curl.setopt(pycurl.CONNECTTIMEOUT, 30)

            curl.setopt(pycurl.FOLLOWLOCATION, 1)
            curl.setopt(pycurl.MAXREDIRS, 5)
            curl.setopt(pycurl.NOSIGNAL, 1)

        return curl

    def get_info(self):
        "状态码 连接时间 接收到第一个字节的时间 总时间"
        monitor = namedtuple("Monitor", ["http_code", "connect_time", "starttransfer_time", "total_time"])
        http_code = self.curl.getinfo(pycurl.HTTP_CODE)
        http_conn_time = self.curl.getinfo(pycurl.CONNECT_TIME)
        http_pre_tran = self.curl.getinfo(pycurl.PRETRANSFER_TIME)
        http_start_tran = self.curl.getinfo(pycurl.STARTTRANSFER_TIME)
        http_total_time = self.curl.getinfo(pycurl.TOTAL_TIME)
        http_size = self.curl.getinfo(pycurl.SIZE_DOWNLOAD)
        body = self.buffer.getvalue()
        return monitor(http_code, http_conn_time, http_start_tran, http_total_time)
