import re

from pprint import pprint
from ipaddress import ip_address


url_list = """https://me.baojia.com/
http://RS-ip:8080/index/treadsInfo
http://me.baojia.com/bike/search/adCode?latitude=39&longitude=116

http://me.baojia.com/bike/get/joinProduct?joinYear=1
https://me.baojia.com/bike/about/us?appFrom=1
"server   https://bat.baojia.com/content/index
后台     http://www.ht.meboth.com/backstage-cupboard-api/sys/index"
http://211.151.2.246:38026
https://batops.baojia.com/operation/battery/model/list
http://hrms.meboth.com/hrms-api/position/getPositionNameList
http://me.baojia.com/pmall/allProduct
http://10.1.11.31:8080/#/dashboard
http://duanxin.baojia.com/sms/sendMsg
"http://static.meboth.cn/xiaomi/metripapp/20180913/rule.html
http://www.hd.meboth.com"
"rcs   http://10.1.11.56:8080/
ibs   http://ibs.baojia.com/ibs/api/brandlist?token=111111"
http://10.1.11.16:8070/signin
http://10.1.11.23:7001
http://dl.baojia.com/auth-api/sys/login
"后台       http://i.meboth.cn/api/mibuUser/notLogin?userId=-1
data-job   http://10.1.11.215:8818/data-job/"
通过api判断
http://cms.baojia.com/backstage-api/bike/getColorList
http://rider.baojia.com/backstage-company-api/companyusers/list
"http://RS-ip:8080/nodeInf
http://RS-ip:8081/nodeInf"
http://RS-ip:8080/info
http://me.baojia.com/join/get/joinProduct
http://wechat.baojia.com/zhanggui-java/auth
http://10.1.11.166:8899/api/jobs/config/baojia.task.RentOrderIllegalDataflowJob
http://pj.baojia.com/bikeparts-api/sys/menu/listUserMenus
http://10.1.11.160:8081/cat/r
http://distribute.baojia.com/info
http://zg.baojia.com/api/get/city/all
"http://creditcrc.baojia.com/crc/verifyIdCardInfo
http://jk.baojia.com/monitor/bike/getBrandList"
curl -XPOST -d '{"frm":"tmp","carId":"864376046631916"}' -H "Content-Type:application/json" http://wangguan.baojia.com/appQuery/btMac
47.95.64.117
47.95.170.94:8677
47.95.69.153:8678
"""

p = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
li_urls = url_full.splitlines()

for i in li_urls:
    print(i)
    # s = p.findall(i)
    # print(s)


def url_find(url_list):
    li_urls = url_list.splitlines()
    all_urls = []
    p = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
    for i in li_urls:
        url_dict = {}
        try:
            if p.findall(i):
                url = p.findall(i)
                url_dict['url'] = url
            elif ip_address(i):
                url_dict['url'] = i
        except Exception as e:
            pass
        else:
            all_urls.append(url_dict)

    pprint(all_urls)

# url_find(url_list)
