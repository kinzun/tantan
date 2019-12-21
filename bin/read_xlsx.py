from collections import namedtuple
import re
import os
import sys
import chardet
import xlrd

from pprint import pprint
from ipaddress import ip_address
import ipaddress

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_DIR)

__all__ = ['ret_urls']


def file_encoding(filename):
    '''解决系统编码文件，WINGBK2312 ,mac utf-8'''
    bytes = min(32, os.path.getsize(filename))
    raw = open(filename, 'rb').read(bytes)
    result = chardet.detect(raw)
    encoding = result['encoding']
    print(encoding)
    infile = open(filename, mode="r", encoding=encoding)
    # data = infile.read()
    # infile.close()

    return infile


# file_encoding('urls.xlsx')


def read_xlsx():
    # data = xlrd.open_workbook('bin/urls_alone.xlsx')
    data = xlrd.open_workbook(os.path.join(BASE_DIR, "urls_alone.xlsx"))
    table = data.sheet_by_name(u'Sheet1')  # 通过名称获取
    nrows = table.nrows
    # 循环行列表数据

    url_info = namedtuple('urls_info', ['name', 'url', 'return_msg', 'code', 'real_host', 'res_type'])
    all_dict_url = []
    for i in range(1, nrows):

        tu = url_info(*map(lambda x: str(x).strip(), table.row_values(i)))
        # tu = url_info(*table.row_values(i))
        if all([tu.name, tu.code, tu.real_host]):
            all_dict_url.append(tu)
    return all_dict_url


def is_ip_Valid(ipaddr):
    try:
        ipaddress.ip_address(ipaddr);
        return True;
    except:
        return False;


def ret_urls():
    """获取xlsx url """
    full_tuple = read_xlsx()
    new_url = []
    url_info = namedtuple('urls_info', ['name', 'url', 'return_msg', 'code', 'real_host', 'res_type'])
    p = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
    for i in full_tuple:
        try:
            if p.findall(i.url):
                url = p.findall(i.url)
            elif is_ip_Valid(i):
                url = i.url
            else:
                url = i.url

            if isinstance(i.code, str):
                code = i.code.split()
                if len(code) >= 2:
                    code = list(map(lambda x: int(float(x)), code))
                else:
                    code = [int(float(code[0]))]

            # 处理后重新生成新的 nametuptupel
            new_url.append(url_info(i.name, url if isinstance(url, list) else [url], i.return_msg, code,
            # new_url.append(url_info(i.name, url if isinstance(url, list) else [url], i.return_msg.split('\n'), code,
                                    i.real_host.split(), i.res_type))

        except Exception as e:
            print(e)

    return new_url


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


def main():
    all_urls_tuple = ret_urls()
    pprint(all_urls_tuple)


if __name__ == "__main__":
    main()
