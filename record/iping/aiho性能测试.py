import asyncio
import requests
import json
import pymysql
from aiohttp import ClientSession, TCPConnector
from datetime import datetime

# 数据库配置
HOST = '127.0.0.1'
PORT = 13306
USER = 'root'
PASSWORD = '123456'
DB = 'testDB'
CHARSET = 'utf8'
PASSWORD_LOGIN_REGISTER = "123456"

# 注册登录配置
URL_LOGIN = "https://test.test.com/user/login"
URL_REGISTER = "https://test.test.com/user"
APP_ID = "testAppId"
APP_SECRET = "testAppSecret"


async def register_user(firstname, lastname, password, nickname, phone, session, i):
    start_time = datetime.now()
    h = {
        "Content-Type": "application/json"
    }
    d = {
        "oemid": "xxx",
        "appid": APP_ID,
        "appsecret": APP_SECRET,
        "firstname": firstname,
        "lastname": lastname,
        "nickname": nickname,
        "password": password,
        "phone": phone,
    }
    try:
        async with session.post(url=URL_REGISTER, data=json.dumps(d), headers=h) as response:
            r = await response.read()
            end_time = datetime.now()
            msg = "第%d个注册请求，开始时间：%s, 花费时间: %d, 返回信息: %s\n" % (i, start_time, cost, r.decode())
            print("running %d" % i, datetime.now())
    except Exception as e:
        print("running %d" % i)
        msg = "%d出问题了" % i + str(e) + "\n"
    with open("log", "a+", encoding="utf-8") as f:
        f.write(msg)


async def bound_register(sem, firstname, lastname, nickname, phone, password, session, i):
    # 使用Semaphore， 它会在第一批2000个请求发出且返回结果(是否等待返回结果取决于你的register_user方法的定义)后
    # 检查本地TCP连接池(最大2000个)的空闲数(连接池某个插槽是否空闲，在这里，取决于请求是否返回)
    # 有空闲插槽，就PUT入一个请求并发出(完全不同于Jmeter的rame up in period的线性发起机制).
    # 所以，在结果log里，你会看到第一批请求(开始时间)是同一秒发起，而后面的则完全取决于服务器的吞吐量
    async with sem:
        await register_user(firstname, lastname, password, nickname, phone, session, i)


async def run(num):
    tasks = []
    # Semaphore， 相当于基于服务器的处理速度和测试客户端的硬件条件，一批批的发
    # 直至发送完全部（下面定义的number/num）
    sem = asyncio.Semaphore(3000)
    # 创建session，且对本地的TCP连接不做限制limit=0
    # 超时时间指定
    # total:全部请求最终完成时间
    # connect: aiohttp从本机连接池里取出一个将要进行的请求的时间
    # sock_connect：单个请求连接到服务器的时间
    # sock_read：单个请求从服务器返回的时间
    timeout = ClientTimeout(total=300, connect=60, sock_connect=60, sock_read=60)
    async with ClientSession(connector=TCPConnector(limit=0), timeout=timeout) as session:
        for i in range(0, num):
            # 如果是分批的发，就使用并传递Semaphore
            task = asyncio.ensure_future(
                bound_register(sem=sem, firstname=str(18300000000 + i), lastname=str(18300000000 + i),
                               nickname=str(18300000000 + i), phone=str(18300000000 + i), password="123456",
                               session=session, i=i))
            tasks.append(task)
        responses = asyncio.gather(*tasks)
        await responses


number = 100000
loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(number))
loop.run_until_complete(future)
