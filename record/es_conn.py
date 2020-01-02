import time
import os
import json
import sys
from concurrent import futures
import elasticsearch

MAX_WORKERS = 10
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_DIR)


def connet_es(IP):
    es = elasticsearch.Elasticsearch(
        [f"{IP}"],  # 连接集群，以列表的形式存放各节点的IP地址
        # sniff_on_start=True,  # 连接前测试
        # sniff_on_connection_fail=True,  # 节点无响应时刷新节点
        # sniff_timeout=3,  # 设置超时时间
        timeout=1
    )
    try:
        res = es.search(index='product')
        if res:
            return {"ip": IP, "res_code": 1}
        else:
            return {"ip": IP, "res_code": 0}
    except Exception as e:
        return {"ip": IP, "res_code": 0}


def thread_many(ES_IP_LIST: list, ):
    workers = min(MAX_WORKERS, len(ES_IP_LIST))  # <4>
    # start_time_1 = time.time()
    full_es_info = {}

    with futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures_ = [executor.submit(connet_es, IP=item) for item in
                    ES_IP_LIST]
        for future in futures.as_completed(futures_):
            res_info = future.result()
            if res_info:
                full_es_info[res_info.get('ip')] = res_info

    with open(os.path.join(BASE_DIR, 'es_full_info.json'), mode='w', ) as f:
        json.dump(full_es_info, f, sort_keys=True, indent=4)
    # print("Thread pool execution inhej " + str(time.time() - start_time_1), "seconds")


def file_time_diff():
    return time.time() - os.path.getctime(os.path.join(BASE_DIR, 'es_full_info.json')) >= 30


def main():
    with open(os.path.join(BASE_DIR, 'es_full_info.json'), mode='r')as f:
        time_info = json.load(f)
        try:
            return time_info.get(sys.argv[1]).get('res_code', "")
        except:
            pass


if __name__ == '__main__':
    if file_time_diff():
        """放入需要检测的 IP 地址和端口 """
        thread_many(['10.1.11.147:9200', '10.1.111.147:9200'])
        print(main())
    else:
        print(main())
