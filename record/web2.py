import os
import tornado
import tornado.ioloop
import tornado.web
import requests
from concurrent.futures import ThreadPoolExecutor


class Executor(ThreadPoolExecutor):
    """ 创建多线程的线程池，线程池的大小为10
    创建多线程时使用了单例模式，如果Executor的_instance实例已经被创建，
    则不再创建，单例模式的好处在此不做讲解
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '_instance', None):
            cls._instance = ThreadPoolExecutor(max_workers=10)
        return cls._instance


# 全部协程+异步线程池实现，yield在此的作用相当于回调函数
# 经过压力测试发现，此种方式的性能在并发量比较大的情况下，要远远优于纯协程实现方案
class Haha1Handler(tornado.web.RequestHandler):
    """ 获取域名所关联的IP信息 """
    # executor为RequestHandler中的一个属性，在使用run_on_executor时，必须要用，不然会报错
    # executor在此设计中为设计模式中的享元模式，所有的对象共享executor的值
    executor = Executor()

    @tornado.web.asynchronous  # 异步处理
    @tornado.gen.coroutine  # 使用协程调度
    def get(self):
        """ get 接口封装 """

        # 可以同时获取POST和GET请求参数
        value = self.get_argument("value", default=None)

        result = yield self._process(value)
        self.write(result)

    @tornado.concurrent.run_on_executor  # 增加并发量
    def _process(self, url):
        # 此处执行具体的任务
        try:
            resp = requests.get(url)
        except IOError as e:
            print(e)
            return 'failed'

        return 'success'


# 全部协程实现
class Haha2Handler(tornado.web.RequestHandler):
    """ 获取域名所关联的IP信息 """

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """ get 接口封装 """

        # 可以同时获取POST和GET请求参数
        value = self.get_argument("value", default=None)

        result = yield tornado.gen.Task(self._process, value)
        self.write(result)

    @tornado.gen.coroutine  # 使用协程调度
    def _process(self, url):
        # 此处执行具体的任务
        try:
            resp = requests.get(url)
        except IOError as e:
            print(e)
            return 'failed'

        return 'success'


class WebServerApplication(object):
    def __init__(self, port):
        self.port = port
        self.settings = {'debug': False}

    def make_app(self):
        """ 构建Handler
        (): 一个括号内为一个Handler
        """

        return tornado.web.Application([
            (r"/gethaha1?", Haha1Handler),
            (r"/gethaha2?", Haha2Handler),
        ], **self.settings)

    def process(self):
        """ 构建app, 监听post, 启动服务 """

        app = self.make_app()
        app.listen(self.port)
        tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    # 定义服务端口
    server_port = "10001"
    server = WebServerApplication(server_port)
    server.process()
