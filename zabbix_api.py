"""zabbix api 调用
# https://github.com/lukecyca/pyzabbix

"""

import logging
import requests
import json


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
        # return self.zapi.graph.get(**params)

        return ZabbixAPIObjectClass(attr, self)


class ZabbixAPIObjectClass(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        """Dynamically create a method (ie: get)"""
        """( host.get)"""

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
        通过主机名称 如 1-11-57 ，获取zbbix 中 主机 id

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
            "type": 7,  # 主动模式客户端
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

        if kwargs.get('name', ''):
            params.get('search').update(**kwargs) if kwargs.get('name') else params.get('search').update(key_=key_)

        return self.zapi.item.get(**params)

    def item_del(self, items):
        "删除主机上的监控项目"

        if not isinstance(items, list):
            items = [items]

        return self.zapi.item.delete(items)

    def item_update(self, itemid=None, **kwargs):
        """更新监控项 设置 """
        """{
            "jsonrpc": "2.0",
            "method": "item.update",
            "params": {
                "itemid": "10092",
                "status": 0
            },
            "auth": "700ca65537074ec963db7efabda78259",
            "id": 1
            }
         """
        params = {
            "itemid": itemid
        }
        if kwargs:
            params.update(**kwargs)

        return self.zapi.item.update(**params)

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

    def get_triggers(self, **kwargs):
        """获取触发器信息
            https://www.zabbix.com/documentation/3.4/zh/manual/api/reference/trigger/get
         """
        params = {
            # "triggerids": "14062",
            "output": "extend",
            # "selectFunctions": "extend"
        }
        params.update(kwargs)

        return self.zapi.trigger.get(**params)

    def update_triggers(self, **kwargs):
        """更新"""
        params = {
            # "triggerid": "13938",
            # "status": 0
        }
        params.update(kwargs)
        return self.zapi.trigger.update(**params)

    def create_triggers(self, description, exp):
        """创建触发器"""
        params = [
            {

                # "description": "Processor load is too high on {HOST.NAME}",
                # "expression": "{Linux server:system.cpu.load[percpu,avg1].last()}>5",

                "description": description,
                "expression": exp,
                # 依赖
                # "dependencies": [
                #     {
                #         "triggerid": "17367"
                #     }
                # ]
            }]
        """
         {
             "description": "Service status",
             "expression": "{Linux server:log[/var/log/system,Service .* has stopped].strlen()}<>0",
             "dependencies": [
                 {
                     "triggerid": "17368"
                 }
             ],
             "tags": [
                 {
                     "tag": "service",
                     "value": "{{ITEM.VALUE}.regsub(\"Service (.*) has stopped\", \"\\1\")}"
                 },
                 {
                     "tag": "error",
                     "value": ""
                 }
             ]]
        """

        return self.zapi.trigger.create(params)

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
