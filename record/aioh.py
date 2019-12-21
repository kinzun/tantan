import asyncio
import aiohttp
from aiohttp.resolver import AsyncResolver
import concurrent

import requests

url = "http://www.baidu.com"


async def fetch_async(url):
    resolver = AsyncResolver(nameservers=["8.8.8.8", "8.8.4.4"])
    conn = aiohttp.TCPConnector(resolver=resolver)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            async with session.get(url, timeout=10) as resp:
                print(resp.headers)
        except concurrent.futures._base.TimeoutError as e:
            print('chao',e)

    # print(resp.status)
    # print(await resp.headers)


tasks = [fetch_async('http://www.google.com/'), fetch_async('http://www.cnblogs.com/ssyfj/'),
         fetch_async('http://baojia.com')]

event_loop = asyncio.get_event_loop()
results = event_loop.run_until_complete(asyncio.gather(*tasks))
event_loop.close()
