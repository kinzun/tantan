# author: Happy
# 来自Happy试验试验 http://happylab.blog.51cto.com
# 脚本主要用于做ping测试

import re
import subprocess


def check_alive(ip, count=1, timeout=1):
    '''
    ping网络测试,通过调用ping命令,发送一个icmp包，从结果中通过正则匹配是否有100%关键字，有则表示丢包，无则表示正常
    '''
    cmd = 'ping -c %d -w %d %s' % (count, timeout, ip)

    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True
                         )

    result = p.stdout.read()
    regex = re.findall('100% packet loss', result)
    if len(regex) == 0:
        print
        "\033[31m%s UP\033[0m" % (ip)
    else:
        print
        "\033[32m%s DOWN\033[0m" % (ip)


if __name__ == "__main__":

    with file('/root/ip.txt', 'r') as f:
        for line in f.readlines():
            ip = line.strip()
            check_alive(ip)  # 执行函数功能调用
