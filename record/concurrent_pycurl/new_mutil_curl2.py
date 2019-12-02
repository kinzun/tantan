from io import BytesIO

import certifi
import pycurl


class Mutio_curl():
    USER_AGENT = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}

    def __init__(self, url):
        c = pycurl.Curl()  # 通过curl方法构造一个对象
        c.setopt(pycurl.FOLLOWLOCATION, True)  # 自动进行跳转抓取
        c.setopt(pycurl.MAXREDIRS, 5)  # 设置最多跳转多少次
        c.setopt(pycurl.CONNECTTIMEOUT, 60)  # 设置链接超时
        c.setopt(pycurl.TIMEOUT, 120)  # 下载超时
        c.setopt(pycurl.ENCODING, 'gzip,deflate')  # 处理gzip内容
        # c.setopt(c.PROXY,ip)  # 代理
        c.fp = BytesIO()
        c.setopt(pycurl.URL, url)  # 设置要访问的URL
        c.setopt(pycurl.USERAGENT, self.USER_AGENT)  # 传入ua
        # c.setopt(pycurl.HTTPHEADER,self.headers)     #传入请求头
        c.setopt(c.WRITEFUNCTION, c.fp.write)  # 回调写入字符串缓存
        c.perform()
        code = c.getinfo(c.HTTP_CODE)  # 返回状态码
        html = c.fp.getvalue()  # 返回源代码


# s = Mutio_curl('http://127.0.0.1:8082')
# print(s)


class Muti_curl():


    def __init__(self, url):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.CAINFO, certifi.where())
        c.perform()
        # c.close()

        http_code = c.getinfo(pycurl.HTTP_CODE)
        http_conn_time = c.getinfo(pycurl.CONNECT_TIME)
        http_pre_tran = c.getinfo(pycurl.PRETRANSFER_TIME)
        http_start_tran = c.getinfo(pycurl.STARTTRANSFER_TIME)
        http_total_time = c.getinfo(pycurl.TOTAL_TIME)
        http_size = c.getinfo(pycurl.SIZE_DOWNLOAD)
        print('http_code: \n http_size conn_time pre_tran start_tran total_time')
        print("%d %d %f %f %f %f" % (
            http_code, http_size, http_conn_time, http_pre_tran, http_start_tran, http_total_time))

        body = buffer.getvalue()
        # Body is a byte string.
        # We have to know the encoding in order to print it to a text file
        # such as standard output.
        # print(body.decode('iso-8859-1'))
        c.close()

    def structure(self,url):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.CAINFO, certifi.where())
        c.perform()
        # c.close()

        http_code = c.getinfo(pycurl.HTTP_CODE)
        http_conn_time = c.getinfo(pycurl.CONNECT_TIME)
        http_pre_tran = c.getinfo(pycurl.PRETRANSFER_TIME)
        http_start_tran = c.getinfo(pycurl.STARTTRANSFER_TIME)
        http_total_time = c.getinfo(pycurl.TOTAL_TIME)
        http_size = c.getinfo(pycurl.SIZE_DOWNLOAD)
        print('http_code: \n http_size conn_time pre_tran start_tran total_time')
        print("%d %d %f %f %f %f" % (
            http_code, http_size, http_conn_time, http_pre_tran, http_start_tran, http_total_time))

        body = buffer.getvalue()
        # Body is a byte string.
        # We have to know the encoding in order to print it to a text file
        # such as standard output.
        # print(body.decode('iso-8859-1'))
        c.close()

        return

