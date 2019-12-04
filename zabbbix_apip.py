import logging
import re
from collections import namedtuple

import requests
import json
from bin.read_xlsx import ret_urls


class _NullHandler(logging.Handler):
    def emit(self, record):
        pass


logger = logging.getLogger(__name__)
logger.addHandler(_NullHandler())


class ZabbixAPIException(Exception):
    """ generic zabbix api exception
    code list:
         -32700 - invalid JSON. An error occurred on the server while parsing the JSON text (typo, wrong quotes, etc.)
         -32600 - received JSON is not a valid JSON-RPC Request
         -32601 - requested remote-procedure does not exist
         -32602 - invalid method parameters
         -32603 - Internal JSON-RPC error
         -32400 - System error
         -32300 - Transport error
         -32500 - Application error
    """
    pass


class ZabbixAPI(object):
    def __init__(self,
                 server='http://localhost/zabbix',
                 session=None,
                 use_authenticate=False,
                 timeout=None):
        """
    Parameters:
            server: Base URI for zabbix web interface (omitting /api_jsonrpc.php)
            session: optional pre-configured requests.Session instance
            use_authenticate: Use old (Zabbix 1.8) style authentication
            timeout: optional connect and read timeout in seconds, default: None (if you're using Requests >= 2.4 you can set it as tuple: "(connect, read)" which is used to set individual connect and read timeouts.)
        """

        if session:
            self.session = session
        else:
            self.session = requests.Session()

        # Default headers for all requests
        self.session.headers.update({
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/pyzabbix',
            'Cache-Control': 'no-cache'
        })

        self.use_authenticate = use_authenticate
        self.auth = ''
        self.id = 0

        self.timeout = timeout

        self.url = server + '/api_jsonrpc.php' if not server.endswith('/api_jsonrpc.php') else server
        logger.info("JSON-RPC Server Endpoint: %s", self.url)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if isinstance(exception_value, (ZabbixAPIException, type(None))):
            if self.is_authenticated:
                self.user.logout()
            return True

    def login(self, user='', password=''):
        """Convenience method for calling user.authenticate and storing the resulting auth token
           for further commands.
           If use_authenticate is set, it uses the older (Zabbix 1.8) authentication command
           :param password: Password used to login into Zabbix
           :param user: Username used to login into Zabbix
        """

        # If we have an invalid auth token, we are not allowed to send a login
        # request. Clear it before trying.
        self.auth = ''
        if self.use_authenticate:
            self.auth = self.user.authenticate(user=user, password=password)
        else:
            self.auth = self.user.login(user=user, password=password)

    def check_authentication(self):
        """Convenience method for calling user.checkAuthentication of the current session"""
        return self.user.checkAuthentication(sessionid=self.auth)

    @property
    def is_authenticated(self):
        try:
            self.user.checkAuthentication(sessionid=self.auth)
        except ZabbixAPIException:
            return False
        return True

    def confimport(self, confformat='', source='', rules=''):
        """Alias for configuration.import because it clashes with
           Python's import reserved keyword
           :param rules:
           :param source:
           :param confformat:
        """

        return self.do_request(
            method="configuration.import",
            params={"format": confformat, "source": source, "rules": rules}
        )['result']

    def api_version(self):
        return self.apiinfo.version()

    def do_request(self, method, params=None):

        if isinstance(params, tuple):
            params = list(*params)

        request_json = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params or {},
            'id': self.id,
        }

        # We don't have to pass the auth token if asking for the apiinfo.version or user.checkAuthentication
        if self.auth and method != 'apiinfo.version' and method != 'user.checkAuthentication':
            request_json['auth'] = self.auth

        logger.debug("Sending: %s", json.dumps(request_json,
                                               indent=4,
                                               separators=(',', ': ')))

        response = self.session.post(
            self.url,
            data=json.dumps(request_json),
            timeout=self.timeout
        )
        logger.debug("Response Code: %s", str(response.status_code))

        # NOTE: Getting a 412 response code means the headers are not in the
        # list of allowed headers.
        response.raise_for_status()

        if not len(response.text):
            raise ZabbixAPIException("Received empty response")

        try:
            response_json = json.loads(response.text)
        except ValueError:
            raise ZabbixAPIException(
                "Unable to parse json: %s" % response.text
            )
        logger.debug("Response Body: %s", json.dumps(response_json,
                                                     indent=4,
                                                     separators=(',', ': ')))

        self.id += 1

        if 'error' in response_json:  # some exception
            if 'data' not in response_json['error']:  # some errors don't contain 'data': workaround for ZBX-9340
                response_json['error']['data'] = "No data"
            msg = u"Error {code}: {message}, {data}".format(
                code=response_json['error']['code'],
                message=response_json['error']['message'],
                data=response_json['error']['data']
            )
            raise ZabbixAPIException(msg, response_json['error']['code'])

        return response_json

    def __getattr__(self, attr):
        """Dynamically create an object class (ie: host)"""

        return ZabbixAPIObjectClass(attr, self)


class ZabbixAPIObjectClass(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        """Dynamically create a method (ie: get)"""

        def fn(*args, **kwargs):
            if args and kwargs:
                raise TypeError("Found both args and kwargs")

            return self.parent.do_request(
                '{0}.{1}'.format(self.name, attr),
                args or kwargs
            )['result']

        return fn


class Moniter(object):

    def __new__(cls, *args, **kwargs):
        instance = super(Moniter, cls).__new__(cls)
        url = 'http://10.1.11.5:8090/api_jsonrpc.php'
        "http://10.1.11.5:8090/zabbix/api_jsonrpc.php"
        username = 'Admin'
        password = 'Baojia.zabbix'
        instance.initialize(url, username, password)
        return instance

    def initialize(self, url, username, password):
        self.hostid = None
        zapi = ZabbixAPI(url)
        zapi.login(username, password)
        print("Connected to Zabbix API Version %s" % zapi.api_version())
        self.zapi = zapi

    def get_groups_id(self):
        """查看主机所属的主机组"""
        hostgroup = {
            "output": ["hostid"],
            "selectGroups": "extend",
            "filter": {
                "host": [
                    "1-11-57"
                ]
            }
        }
        return self.zapi.host.get(**hostgroup)

    def get_host_id(self, name=""):
        """

        :param name:  主机名称
        :return:  返回主机id
        """
        hostid = []
        for i in self.get_all_host():
            # print(i['name'])
            if name in i['name']:
                hostid.append(i['hostid'])
                break
        self.hostid = hostid[0]
        return hostid[0]

    def get_all_host(self):
        """获取所有主机"""
        return self.zapi.host.get(output="extend")

    def item_create(self, item_name, key_name, value_type=0, hostid=None):
        """
        创建监控项
        Value_type 3 整数
        value_type  0 浮点	
        """

        if not hostid:
            hostid = self.hostid
        # hostid = "10452"  # 57

        params = {
            "name": item_name,
            "key_": key_name,
            "hostid": hostid,
            "type": 0,
            "interfaceid": "178",
            "value_type": value_type,
            "delay": "60s",
            "inventory_link": 0,
        }
        if value_type == 0:
            params.update({"units": "s"})
        # if "real" in key_name and not "code" in key_name:
        #     params.update({"units": "s"})

        return self.zapi.item.create(**params)

    def item_get(self, hostid=None, key_="health", **kwargs, ):
        """获取监控项"""
        # hostid = "10452"  # 57
        if not hostid:
            hostid = self.hostid

        params = {
            "output": "extend",
            "hostids": hostid,
            "search": {
                # "key_": key_  # 通过key 查询
                # "name": key_  # 通过key 查询
            },
            "sortfield": "name"  # 名称排序
        }

        params.get('search').update(**kwargs) if kwargs.get('name') else params.get('search').update(key_=key_)

        return self.zapi.item.get(**params)

    def item_del(self, items):
        "删除主机上的监控项目"

        if not isinstance(items, list):
            items = [items]

        return self.zapi.item.delete(items)

    def graph_get(self):
        """获取主机上的图形"""
        params = {
            "output": "extend",
            "hostids": self.hostid,
            "sortfield": "name"
        }

        return self.zapi.graph.get(**params)

    def graph_create(self, name, gitems):
        """图形创建， 颜色线条"""

        params = {
            "name": name,
            "width": 900,
            "height": 200,
            "gitems": gitems

            # "gitems": [
            #     {
            #         "itemid": "22828",
            #         "color": "00AA00"
            #     },
            #     {
            #         "itemid": "22829",
            #         "color": "3333FF"
            #     }
            # ]
        }
        return self.zapi.graph.create(**params)

    def graphitem_get(self, graphid):
        """查看图形 监控项 ，颜色"""
        params = {
            "output": "extend",
            "graphids": graphid
        }
        return self.zapi.graphitem.get(**params)

    @property
    def choose_color(self):
        """http://blog.sina.com.cn/s/blog_a7b297ed0102ww2v.html
        https://matplotlib.org/devdocs/gallery/showcase/bachelors_degrees_by_gender.html#sphx-glr-gallery-showcase-bachelors-degrees-by-gender-py
        """

        """颜色线条"""
        color_sequence = ['#dbdb8d', '#17becf', '#ff9896', '#199C0D', '#1f77b4', '#aec7e8', '#ff7f0e', '#c5b0d5',
                          '#ffbb78', '#98df8a', "#9edae5", '#d62728', '#9467bd', '#bcbd22', '#8c564b',
                          '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7']

        return [_.replace("#", "") for _ in color_sequence]


class Create_Batch(object):

    #
    # def __new__(cls, *args, **kwargs):
    #     instance = super(Create_Batch, cls).__new__(cls)
    #
    #
    #     return instance
    # def initialize(self):
    #     zbix = Moniter()
    #     zbix.hostid = "10452"
    #

    @staticmethod
    def create_batch_item():
        """批量创建 监控项目 名称 和键值"""
        zbix = Moniter()

        all_state = [("health_total_{}", "health_total[{}]"), ("health_code_{}", "health_code[{}]"),
                     ("health_connect_{}", "health_connect[{}]"), ("health_start_{}", "health_start[{}]")]

        from bin.read_xlsx import ret_urls
        urls = ret_urls()

        for i in urls:
            for name in all_state:
                try:
                    itemname = name[0].format(i.url[0])
                    key_name = name[1].format(i.url[0])
                    if "code" in name[0]:
                        zbix.item_create(item_name=itemname,
                                         key_name=key_name, value_type=3)
                    else:
                        zbix.item_create(item_name=itemname,
                                         key_name=key_name)
                except Exception as e:
                    print(e)

    @staticmethod
    def create_batch_graph():
        """创建图形"""
        urls_info = ret_urls()
        zbix = Moniter()
        zbix.hostid = "10452"

        for it in urls_info:
            try:
                items = zbix.item_get(key_=it.url)
                graph_items = [{'itemid': i.get('itemid')} for i in items]
                colors = [{'color': '199C0D'}, {'color': 'F63100'}, {'color': '2774A4'}, {'color': 'F7941D'}]
                for i in range(len(colors)):
                    graph_items[i].update(colors[i])
                res = zbix.graph_create(name=it.name, gitems=graph_items)

                print(res)
            except  Exception as e:
                print(e)

    @staticmethod
    def _create_test():
        """中断 搜索"""
        zbix = Moniter()
        hostid = zbix.get_host_name("Meboth-IDC-Switch-1")
        all_graphics_received = zbix.item_get(hostid, key_="Bits received")
        import re
        sind = re.compile(
            # r"Interface GigabitEthernet1/0/.*\(GigabitEthernet1/0/[1-9]{1}.* Interface\): Bits received")
            # r"Interface GigabitEthernet.*\(D_BJ-MiBuKeJi-FW:.*\): Bits received")
            r"D_BJ-MiBuKeJi-FW")
        # r"Interface GigabitEthernet1/0/(10|[1-9])\(D_BJ-MiBuKeJi-FW:1-G1/0/[1-9]{1}.*\): Bits sent")
        # r"Interface GigabitEthernet1/0/(10|[1-9])\(D_BJ-MiBuKeJi-FW:1-G1/0/.*\): Bits received")
        # r"Interface GigabitEthernet(10|[1-9]){1}/0/48\(D_BJ-MiBuKeJi-FW:(10|[1-9])-G1/0/15\): Bits received")

        # "nterface GigabitEthernet1/0/(10|[1-9])\(D_BJ-MiBuKeJi-FW:1-G1/0/.*\): Bits received"
        for i in all_graphics_received:
            if sind.findall(i.get('name')):
                # print(i.get('name'))
                print(i)

    @staticmethod
    def crate_batch_mhost():
        """创建 监控项 多主机 toal code"""
        zbix = Moniter()
        hostid = zbix.get_host_id(name="1-11-57")
        zbix.hostid = hostid
        graph = zbix.graph_get()
        urls_info = ret_urls()

        # pprint(urls_info)

        def code_toal_string(real_backend=None):
            """生成监控项所用的，key  , code total"""
            return [("real_health_code_{}", "real_health_code[{},{}]"),
                    ("real_health_total_{}", "real_health_total[{},{}]")] if real_backend else [
                ("health_code_{}", "health_code[{}]"),
                ("health_total_{}", "health_total[{}]")]

            # else [("health_total_{}", "health_total[{}]"), ("health_code_{}", "health_code[{}]"),
            #       ("health_connect_{}", "health_connect[{}]"), ("health_start_{}", "health_start[{}]")]

        def item_create_(itemname, key_name):
            if "code" in itemname:
                zbix.item_create(item_name=itemname,
                                 key_name=key_name, value_type=3)
            else:
                zbix.item_create(item_name=itemname,
                                 key_name=key_name)

        # items = zbix.item_get(key_=it.url)
        for it in urls_info:
            # if it.url[0] == 'https://me.baojia.com/':
            for name in code_toal_string():
                try:
                    itemname = name[0].format(it.url[0])
                    key_name = name[1].format(it.url[0])
                    item_create_(itemname, key_name)
                except Exception as e:
                    print(e)

            if len(it.real_host) >= 1:
                for i in it.real_host:
                    for name in code_toal_string(real_backend=True):
                        try:
                            itemname = name[0].format(i)
                            key_name = name[1].format(it.url[0], i)
                            item_create_(itemname, key_name)
                        except Exception as e:
                            print(e)

    @staticmethod
    def domain_search():
        pass
        # 域名提取
        # from urllib.parse import urlparse
        # urls_info = ret_urls()
        # for i in urls_info:
        #
        #     res = urlparse(i.url[0])
        #     print(res)

    @staticmethod
    def crate_mhost_grpaph():
        urls_info = ret_urls()
        zbix = Moniter()
        zbix.hostid = "10452"

        for it in urls_info:
            try:
                items_domain = zbix.item_get(name=it.url)
                items_real = (zbix.item_get(name=i) for i in it.real_host)
                print(list(items_real))
                graph_items = [{'itemid': i.get('itemid')} for i in items_domain]
                print(graph_items)

                colors = [{'color': '199C0D'}, {'color': 'F63100'}, {'color': '2774A4'}, {'color': 'F7941D'}]
                for i in range(len(colors)):
                    graph_items[i].update(colors[i])
                res = zbix.graph_create(name=it.name, gitems=graph_items)

                # print(res)
            except  Exception as e:
                print(e)

        pass

    @staticmethod
    def items_del():
        """获取主机上所有监控项，然后删除"""
        zbix = Moniter()
        zbix.hostid = "10452"
        item = zbix.item_get()
        iems = [i.get('itemid') for i in item]
        zbix.item_del(iems)

    @staticmethod
    def crete_mhost_graph_():
        urls_info = ret_urls()
        zbix = Moniter()
        zbix.hostid = "10452"
        s = zbix.graph_get()

        url_info = namedtuple('urls_info', ['name', 'url', 'return_msg', 'code', 'real_host'])

        it = url_info(name='bike-bike', url=['https://me.baojia.com/'], return_msg=['没有相关操作权限'], code=[200],
                      real_host=['10.1.11.140:8080', '10.1.11.220:8080', '10.1.11.221:8080'])

        for it in urls_info:
            # 获取所有 域名下 后端的真实主机
            try:
                # 域名 url
                items_domainip_color = [
                    {'itemid': i.get('itemid'), 'yaxisside': 1 if "health_code_http" in i.get('name') else 0} for i in
                    zbix.item_get(name=it.url[0])]

                all_items_color = [{"color": _} for _ in zbix.choose_color[:len(items_domainip_color)]]

                for i in range(len(items_domainip_color)):
                    items_domainip_color[i].update(all_items_color[i])

                zbix.graph_create(name=f"{it.name}_{it.url[0]}", gitems=items_domainip_color)

                # 后端真实主机监控
                items_real = (zbix.item_get(name=_) for _ in it.real_host)
                realend_items = [
                    {'itemid': item.get('itemid'), 'yaxisside': 1 if "health_code" in item.get('name') else 0}
                    for i in items_real for item in i]
                real_end_color = [{"color": _} for _ in zbix.choose_color[:len(realend_items)]]
                for i in range(len(realend_items)):
                    realend_items[i].update(real_end_color[i])

                zbix.graph_create(name=f"realend_{it.name}_{it.url[0]}", gitems=realend_items)


            except  Exception as e:
                print(e)
                pass

    @staticmethod
    def create_ms_graph():

        urls_info = ret_urls()
        zbix = Moniter()
        zbix.hostid = "10452"
        s = zbix.graph_get()

        url_info = namedtuple('urls_info', ['name', 'url', 'return_msg', 'code', 'real_host'])

        it = url_info(name='bike-bike', url=['https://me.baojia.com/'], return_msg=['没有相关操作权限'], code=[200],
                      real_host=['10.1.11.140:8080', '10.1.11.220:8080', '10.1.11.221:8080'])

        for it in urls_info:

            # 获取所有 域名下 后端的真实主机
            try:
                items_domainip_color = [
                    {'itemid': i.get('itemid'), 'yaxisside': 1 if "health_code_http" in i.get('name') else 0} for i in
                    zbix.item_get(name=it.url[0]) if re.findall(r"{}$".format(it.url[0]), i.get("name"))]
                # 后端真实主机监控
                items_real = (zbix.item_get(name=_) for _ in it.real_host)

                # for i in it.real_host:
                #     all_real_host = zbix.item_get(name=i)
                #     for item_real in all_real_host:
                #         print(item_real.get('name'))

                # for  item_real in item_real:

                [items_domainip_color.append(
                    {'itemid': item.get('itemid'), 'yaxisside': 1 if "health_code" in item.get('name') else 0}) for i
                    in
                    items_real for item in i if item.get('name').startswith('real')]
                all_items_color = [{"color": _} for _ in zbix.choose_color[:len(items_domainip_color)]]
                for i in range(len(items_domainip_color)):
                    items_domainip_color[i].update(all_items_color[i])

                print(items_domainip_color)
                res = zbix.graph_create(name=f"{it.name}_{it.url[0]}", gitems=items_domainip_color)
                # print(res)

            except  Exception as e:
                print(e)
                pass


if __name__ == '__main__':
    from pprint import pprint

    mutil_cr = Create_Batch()
    mutil_cr.crate_batch_mhost()
    mutil_cr.create_ms_graph()

    # mutil_cr.items_del()

    # zbix.graph_get()

    # zbix.item_get()

    # graph_items = [{'itemid': i.get('itemid')} for i in all_graphics if sind.findall(i.get('name'))]

    # graph_items = [{'itemid': i.get('itemid')} for i in all_graphics if sind.findall(i.get('name'))]
    # res = zbix.graph_create(name=it.name, gitems=graph_items)

    # urls_info = ret_urls()
    #

    # hosts = zapi.host.get(filter={"host": host_name}, selectInterfaces=["interfaceid"])
    # zbix = Moniter()
    # zbix.hostid = "10452"
    # item = zbix.item_get()
    # iems = [i.get('itemid') for i in item]
    # s = zbix.item_del(iems)

    # print(zbix.get_host_name('1-11-57'))
    # print(zbix.get_groups_id())

    # def create_batch_graph():
    #     for i in urls_info:

    # for i in items:
    #     pprint(i)
    # print(i.get('name'))

    # pprint(zbix.graph_get())
    # pprint(zbix.graphitem_get("2296"))

    # pprint(zbix.item_create(item_name="health_totalhttp://10.1.11.160:8081/cat/r",
    #                         key_name="headlth_total[http://10.1.11.160:8081/cat/r]"))

    # Create_Batch.create_batch_graph()
    # #
