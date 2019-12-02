import threading
import pycurl
from collections import namedtuple
import certifi
from io import BytesIO


class Test(threading.Thread):
    def __init__(self, url, target_file, progress):
        threading.Thread.__init__(self)
        self.target_file = target_file
        self.progress = progress
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEDATA, self.target_file)
        self.curl.setopt(pycurl.FOLLOWLOCATION, 1)
        self.curl.setopt(pycurl.NOPROGRESS, 0)
        self.curl.setopt(pycurl.PROGRESSFUNCTION, self.progress)
        self.curl.setopt(pycurl.MAXREDIRS, 5)
        self.curl.setopt(pycurl.NOSIGNAL, 1)

    def run(self):
        self.curl.perform()
        self.curl.close()
        self.target_file.close()
        self.progress(1.0, 1.0, 0, 0)


class Muti_curl():
    def __init__(self, url):
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.URL, url)  # url
        self.curl.setopt(self.curl.URL, url)
        # self.curl.setopt(self.curl.WRITEDATA, buffer)
        self.curl.setopt(self.curl.CAINFO, certifi.where())
        self.curl.perform()

    @classmethod
    def deti(cls):
        # cls.curl.setopt(pycurl.URL, url)  # url
        # self.curl.setopt(pycurl.WRITEDATA, self.target_file),
        cls.curl.setopt(pycurl.FOLLOWLOCATION, 1)
        cls.curl.setopt(pycurl.NOPROGRESS, 0)
        # self.curl.setopt(pycurl.PROGRESSFUNCTION, self.progress)
        cls.curl.setopt(pycurl.MAXREDIRS, 5)
        cls.curl.setopt(pycurl.NOSIGNAL, 1)
        return cls

    def new(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        # c.setopt(c.URL, 'http://pycurl.io/')
        c.setopt(c.URL, 'http://baojia.com/')
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.CAINFO, certifi.where())

    def get_info(self):
        "状态码 连接时间 接收到第一个字节的时间 总时间"
        monitor = namedtuple("Monitor", ["http_code", "connect_time", "starttransfer_time", "total_time"])
        http_code = self.curl.getinfo(pycurl.HTTP_CODE)
        http_conn_time = self.curl.getinfo(pycurl.CONNECT_TIME)
        http_pre_tran = self.curl.getinfo(pycurl.PRETRANSFER_TIME)
        http_start_tran = self.curl.getinfo(pycurl.STARTTRANSFER_TIME)
        http_total_time = self.curl.getinfo(pycurl.TOTAL_TIME)

        print(self.curl.getinfo_raw(pycurl.EFFECTIVE_URL))

        http_size = self.curl.getinfo(pycurl.SIZE_DOWNLOAD)
        return monitor(http_code, http_conn_time, http_start_tran, http_total_time)


url = "http://127.0.0.1:8082/"
# url = "http://www.baojia.com/"
curl = Muti_curl(url)
# s = curl.get_info()
# print(s)
