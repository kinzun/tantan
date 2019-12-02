import pycurl
from io import BytesIO


def multi_curl_request(request_params):
    m = pycurl.CurlMulti()
    reqs = []
    for request_param in request_params:
        c = pycurl.Curl()
        buffer = BytesIO()
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.setopt(c.CONNECTTIMEOUT, 1)  # 1s 连接超时设置
        c.setopt(c.TIMEOUT, 3)  # 3s 整个请求超时设置
        c.setopt(c.CUSTOMREQUEST, request_param["method"])
        c.setopt(c.DNS_CACHE_TIMEOUT, 3600)
        c.setopt(c.URL, request_param['url'])

        buffer = BytesIO()
        c.setopt(c.WRITEFUNCTION, buffer.write)

        m.add_handle(c)
        req = [buffer, c]
        reqs.append(req)

    num_handlers = len(reqs)

    while num_handlers:
        ret = m.select(2.0)
        if ret == -1:  # 请求超时标记
            continue
        while 1:
            ret, num_handlers = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM: break

    resps = []
    for req in reqs:
        resp, c = req
        http_code = c.getinfo(c.HTTP_CODE)
        http_body = resp.getvalue()
        content_type = c.getinfo(c.CONTENT_TYPE)
        http_headers = {'Content-Type': content_type}

        curl_info = {
            'url': c.getinfo(c.EFFECTIVE_URL),
            'connect_time': c.getinfo(c.CONNECT_TIME),
            'namelookup_time': c.getinfo(c.NAMELOOKUP_TIME),
            'total_time': c.getinfo(c.TOTAL_TIME),
        }

        resps.append([http_code, http_body, http_headers, curl_info])
    return resps


b = {"url": "http://127.0.0.1:8082", "method": "get"}

multi_curl_request(b)
# multi_curl_request(['http://127.0.0.1:8082/'] * 10)
