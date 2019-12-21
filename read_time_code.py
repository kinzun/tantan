import time
import json
import sys
import os
from run_m import tornado_curl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)

url_time_info = os.path.join(BASE_DIR, 'url_time_info.json')


def file_time_diff():
    return time.time() - os.path.getctime(url_time_info) >= 30


def main():
    # if file_time_diff():
    #     tornado_curl.run()

    with open(url_time_info, mode='r')as f:
        time_info = json.load(f)
        if len(sys.argv) >= 3:
            try:
                return time_info.get(sys.argv[1])['backend_real'].get(sys.argv[2]).get('code', "")
            except Exception as e:
                print(e)
                return ""
        else:
            return time_info.get(sys.argv[1]).get('code', "")


print(main())
