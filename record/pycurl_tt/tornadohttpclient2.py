from tornado.httpclient import AsyncHTTPClient
from tornado import ioloop


async def f():
    http_client = AsyncHTTPClient()
    try:
        response = await http_client.fetch("http://www.baidu.com")
    except Exception as e:
        print("Error: %s" % e)
    else:
        print(response.request_time)
        print(response.start_time)
        print(response.effective_url)
        print(response.code)
        print(response.reason)
        # print(response.body)


io_loop = ioloop.IOLoop.current()
io_loop.run_sync(f)
