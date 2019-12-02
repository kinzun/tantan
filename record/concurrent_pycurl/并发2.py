import pycurl
import pycurl
import certifi
from io import BytesIO


def set():
    # ! /usr/bin/env python
    # -*- coding: utf-8 -*-
    # vi:ts=4:et
    buffer = BytesIO()
    c = pycurl.Curl()
    # c.setopt(c.URL, 'http://pycurl.io/')
    c.setopt(c.URL, 'http://baojia.com/')
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
    print("%d %d %f %f %f %f" % (http_code, http_size, http_conn_time, http_pre_tran, http_start_tran, http_total_time))

    body = buffer.getvalue()
    # Body is a byte string.
    # We have to know the encoding in order to print it to a text file
    # such as standard output.
    # print(body.decode('iso-8859-1'))
    c.close()

