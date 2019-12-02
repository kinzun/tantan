import time

from tornado.httpclient import AsyncHTTPClient

from tornado import ioloop
from tornado.ioloop import IOLoop
import asyncio

count = 10
done = 0


def handle_request(response):
    global done
    print(response)
    print('go')
    done += 1
    if (done == count):
        # 结束循环
        IOLoop.instance().stop()

    if response.error:
        print("Error:", response.error)
    else:
        print(response.body)


# 默认client是基于ioloop实现的，配置使用Pycurl
# AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=20)
# http_client = AsyncHTTPClient()
# for i in range(count):
#     http_client.fetch("http://127.0.0.1:8082", handle_request)


# 死循环
# IOLoop.instance().start()

from tornado.curl_httpclient import CurlAsyncHTTPClient


async def fetch_async(url):
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=30)
    http_client = AsyncHTTPClient()
    try:
        response = await http_client.fetch(url, connect_timeout=5)
    except Exception as e:
        print("Error: %s" % e)
        response = {"url": url, "code": e.code, "message": e.message, "total": ''}
        # print(response)
        # {'queue': 5.9604644775390625e-06, 'namelookup': 0.004395, 'connect': 0.010885, 'appconnect': 0.0,
        #  'pretransfer': 0.010935, 'starttransfer': 0.313392, 'total': 3.586431, 'redirect': 3.272593}


    else:
        # print(response.headers)
        # print(response.request_time)
        pass
        # print(response.code)
        # print(response.time_info)
        # print(response.start_time)
        # print(response.elapsed.total_seconds())
        # response.time_info[]
    finally:
        if hasattr(response, 'time_info'):
            response.time_info['url'] = url
            dict_info.append(response.time_info)
        else:
            dict_info.append(response)

        # print(response.effective_url)
        # print(response.code)
        # print(response.time_info)
        # print(response.reason)
        # print(response.body)


tasks = [fetch_async('http://www.google.com/'), fetch_async('http://www.cnblogs.com/ssyfj/'),
         fetch_async('http://baojia.com')]

# tasks = [fetch_async("http://127.0.0.1:8082/curl/")] * 50
# tasks = [fetch_async("http://127.0.0.1:8082/curl/") for i in range(50)]
# tasks = [fetch_async("http://baojia.com") for i in range(5)]

# io_loop = ioloop.IOLoop.current()
# io_loop.run_sync()

dict_info = []

start = time.time()
event_loop = asyncio.get_event_loop()
results = event_loop.run_until_complete(asyncio.gather(*tasks))
event_loop.close()
print(time.time() - start)

print(dict_info)


