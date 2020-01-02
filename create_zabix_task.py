import re
import json

from collections import namedtuple
from urllib.parse import urlparse
from urllib.parse import unquote_plus, quote_plus

from zabbix_api import Moniter
from bin.read_xlsx import ret_urls


class Create_Batch(object):

    def __new__(cls, *args, **kwargs):
        instance = super(Create_Batch, cls).__new__(cls)
        instance.initialize()
        return instance

    def initialize(self):
        zbix = Moniter()
        # zbix.hostid = "10452"
        self.zbix = zbix

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
        """未完成， 搜索"""
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
                    itemname_key = map(
                        lambda x: x.format(it.url[0]) if "[" not in x else x.format(quote_plus(it.url[0])), name)
                    item_create_(*itemname_key)
                except Exception as e:
                    print(e)

            if len(it.real_host) >= 1:
                for i in it.real_host:
                    for name in code_toal_string(real_backend=True):
                        try:
                            itemname = name[0].format(i)
                            key_name = name[1].format(quote_plus(it.url[0]), quote_plus(i))
                            item_create_(itemname, key_name)
                        except Exception as e:
                            print(e)

    @staticmethod
    def domain_search():
        # 域名提取
        urls_info = ret_urls()
        for i in urls_info:
            res = urlparse(i.url[0])
            print(res)

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
        """创建图形， 域名和 后端真实主机分别创建图形"""
        urls_info = ret_urls()
        zbix = Moniter()
        zbix.hostid = "10452"
        s = zbix.graph_get()

        url_info = namedtuple('urls_info', ['name', 'url', 'return_msg', 'code', 'real_host'])

        it = url_info(name='bike-bike', url=['https://me.baojia.com/'], return_msg=['没有相关操作权限'], code=[200],
                      real_host=['10.1.11.140:8080', '10.1.11.220:8080', '10.1.11.221:8080'])

        def url_conversion(url, item_name):

            regular = re.compile("(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]")
            if regular.search(item_name):
                re_item_url = regular.findall(item_name)
                if unquote_plus(re_item_url[0]) == unquote_plus(url):
                    return True
            else:
                return item_name

        for it in urls_info:
            # 获取所有 域名下 后端的真实主机
            try:
                # 域名 url
                # items_domainip_color = [
                #     {'itemid': i.get('itemid'), 'yaxisside': 1 if "health_code_http" in i.get('name') else 0} for i in
                #     zbix.item_get(name=it.url[0])]
                print(it.url[0])
                items_domainip_color = [
                    {'itemid': i.get('itemid'), 'yaxisside': 0 if "health_code_http" in i.get('name') else 1,
                     "drawtype": 5 if "health_code_http" in i.get('name') else 1} for i in
                    zbix.item_get(name=it.url[0]) if url_conversion(it.url[0], i.get('name'))]

                all_items_color = [{"color": _} for _ in zbix.choose_color[:len(items_domainip_color)]]

                for i in range(len(items_domainip_color)):
                    items_domainip_color[i].update(all_items_color[i])

                pprint(items_domainip_color)

                zbix.graph_create(name=f"{it.name}_{it.url[0]}", gitems=items_domainip_color)

                # 后端真实主机监控
                items_real = (zbix.item_get(name=_) for _ in it.real_host)

                # realend_items = [
                #     {'itemid': item.get('itemid'), 'yaxisside': 1 if "health_code" in item.get('name') else 0}
                #     for i in items_real for item in i]

                yaxisside_code = lambda x: 0 if "health_code" in x else 1
                drawtype_code = lambda x: 5 if "health_code" in x else 1

                realend_items = [
                    {'itemid': item.get('itemid'), 'yaxisside': yaxisside_code(item.get('name')),
                     'drawtype': drawtype_code(item.get('name'))} for i
                    in
                    items_real for item in i if item.get('name').startswith('real')]

                real_end_color = [{"color": _} for _ in zbix.choose_color[:len(realend_items)]]
                for i in range(len(realend_items)):
                    realend_items[i].update(real_end_color[i])

                zbix.graph_create(name=f"realend_{it.name}_{it.url[0]}", gitems=realend_items)


            except  Exception as e:
                print(e)
                pass

    @staticmethod
    def create_ms_graph():
        """域名和主机的都在一个图形中"""

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
                    zbix.item_get(name=it.url[0]) if re.findall("{}$".format(it.url[0]), i.get("name"))]
                # 后端真实主机监控
                items_real = (zbix.item_get(name=_) for _ in it.real_host)

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

    @staticmethod
    def item_upde_():
        """
        更新主机上所有监控项的类型,为主动模式 type 7
        https://www.zabbix.com/documentation/4.0/manual/api/reference/item/object#item


        :return:
        """

        zbix = Moniter()
        zbix.hostid = "10452"
        all_itemid = (i.get('itemid') for i in zbix.item_get())
        for i in all_itemid:
            try:
                zbix.item_update(i, type=7)
                # zbix.item_update(i, delay="60s")
            except Exception as e:
                print(e)

    def graphitem_get_(self):
        zbix = Moniter()
        zbix.hostid = "10452"

        graph = zbix.graph_get()
        s = (i for i in graph if 'bike-bike' in i.get('name'))
        for i in s:
            print(i)

        mutil_cr = Create_Batch()
        mutil_cr.crete_mhost_graph_()
        pprint(zbix.graphitem_get("3196"))

    def get_triggers(self):

        pass

    def adding_triggers(self):
        pass
        self.zbix.hostid = "10452"

    @staticmethod
    def create_trigger():
        """ 创建 触发器"""
        zbix = Moniter()
        zbix.hostid = "10452"
        # s = zbix.get_triggers(hostids="10452")
        import json
        def read_code_url() -> dict:
            url_code_dict = dict()
            with  open('url_time_info.json')as f:
                all_info = json.load(f)

            for k, v in all_info.items():
                if isinstance(v, dict):
                    alone = url_code_dict[v['url']] = {}
                    alone['url'] = k
                    alone['name'] = v['business_name']
                    alone['code'] = v['code']
            return url_code_dict

        # read_code_url()
        exp_base = "{1-11-57:health_code[%(key)s].last()}<>%(code)s"
        full_exp = exp_base % {"key": '10.1.11.57', "code": 200}
        print(read_code_url())
        for k, v in read_code_url().items():
            try:
                s = zbix.create_triggers(description=v['name'], exp=exp_base % {"key": v['url'], "code": v['code']})
            except Exception as e:
                print(e)

    @staticmethod
    def more_update_trigger():
        """匹配触发更新"""
        zbix = Moniter()
        zbix.hostid = "10452"
        s = zbix.get_triggers(hostids="10452")

        def read_code_url() -> dict:
            url_code_dict = dict()
            with open('url_time_info.json')as f:
                all_info = json.load(f)

            for k, v in all_info.items():
                if isinstance(v, dict):
                    alone = url_code_dict[v['url']] = {}
                    alone['url'] = k
                    alone['name'] = v['business_name']
                    alone['code'] = v['code']
            return url_code_dict

        time_url_info = read_code_url()
        for i in s:
            des = i.get('description')
            triggerid = i.get('triggerid')
            zbix.update_triggers(description=time_url_info.get(des).get('name'), triggerid=triggerid)


if __name__ == '__main__':
    from pprint import pprint

    zbix = Moniter()
    zbix.hostid = "10452"

    zbix.item_get()


    # s = Create_Batch()
    # s.adding_triggers()
    # more_update_trigger()

    # i.get('')

    # s = exp_base.format(key='health_code[10.1.11.57]', code=200)
    # pprint(s)
    # print('{greet} from {language}.'.format(greet='Hello world', language='Python'))
    # s = zbix.create_triggers(description=,exp="{1-11-57:health_code[10.1.11.57].last()}<>200")
    # print(s)

    # print(zbix.get_host_id('1-11-57'))

    # mutil_cr = Create_Batch()
    # mutil_cr.item_upde_()

    # mutil_cr.crate_batch_mhost()
    # mutil_cr.crete_mhost_graph_()
    # mutil_cr.create_ms_graph()

    # mutil_cr.items_del()

    # s = zbix.graph_get()

    # s = zbix.item_get(name='cmdb')

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
