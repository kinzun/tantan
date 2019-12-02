# -*- coding:utf-8 -*-
import re
import urllib

"""
url采集脚本
仅适用于此站点的list，自动翻页采集
http://www.qkankan.com/
"""


def getHtml(url):
    print("hello cdxy\n\ntesting page 1")
    page = urllib.urlopen(url)
    html = page.read()
    for i in range(2, 10000):
        page = urllib.urlopen(url + '/index_' + str(i) + '.html')
        current_html = page.read()
        if 'message.gif' not in current_html:
            html += current_html
            print("gathering urls from page:" + str(i))
        else:
            print("\ntotal_page: " + str(i - 1))
            break

    return html


def getUrl(html):
    reg = r'http://(.*?)(/|\"|\')'  # 正则
    urlre = re.compile(reg)
    urllist = re.findall(urlre, html)
    return urllist


html = getHtml("http://www.qkankan.com/medium/")  # 地址输入
print(html)
# ans = getUrl(html)

# fobj = open('target_list.txt', 'w')  # 输出位置
# ans_list = []
# white_list = ['www.w3.org', 'www.qkankan.com', 'm.qkankan.com']  # 白名单，不作采集
# for each in ans:
#     if each[0] not in ans_list and each[0] not in white_list:
#         ans_list.append(each[0])
#         fobj.write(each[0] + '\n')
# fobj.close()
#
# print("\nOver!\nURLs:" + str(len(ans_list)))
