import json
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)

url_time_info = os.path.join(BASE_DIR, 'url_time_info.json')


# if len(sys.argv) >= 2:
#     item_one = sys.argv[1]
#     item_two = sys.argv[2]


def main():
    with open(url_time_info, mode='r')as f:
        time_info = json.load(f)
        if len(sys.argv) >= 3:
            return time_info.get(sys.argv[1],'')['backend_real'].get(sys.argv[2],'').get('connect', '')
        else:
            return time_info.get(sys.argv[1]).get('connect', '')


print(main())
