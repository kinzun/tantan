from io import BytesIO
import pycurl
from collections import namedtuple


class Muti_curl():
    def __init__(self, url):
        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.URL, url)  # url

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

    """
     
pycurl.Curl() #创建一个pycurl对象的方法
pycurl.Curl(pycurl.URL, http://www.google.com.hk) #设置要访问的URL
pycurl.Curl().setopt(pycurl.MAXREDIRS, 5) #设置最大重定向次数
pycurl.Curl().setopt(pycurl.CONNECTTIMEOUT, 60)
pycurl.Curl().setopt(pycurl.TIMEOUT, 300) #连接超时设置

c.setopt(pycurl.CONNECTTIMEOUT, 60)     #设置链接超时
c.setopt(pycurl.ENCODING, 'gzip,deflate')   #处理gzip内容

pycurl.Curl().setopt(pycurl.USERAGENT, "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)") #模拟浏览器
pycurl.Curl().perform() #服务器端返回的信息
pycurl.Curl().getinfo(pycurl.HTTP_CODE) #查看HTTP的状态 类似urllib中status属性

 """

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
        http_size = self.curl.getinfo(pycurl.SIZE_DOWNLOAD)
        return monitor(http_code, http_conn_time, http_start_tran, http_total_time)


url = "http://127.0.0.1:8082/"
url = "http://www.baojia.com/"
curl = Muti_curl(url)
s = curl.get_info()
print(s)
