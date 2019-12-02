import requests
import datetime
from datetime import timedelta
import time
import sys

preferred_clock = time.time

start = preferred_clock()

# Send the request
# r = adapter.send(request, **kwargs)

# print(time.sleep(10))

# Total elapsed time of the request (approximately)
# elapsed = preferred_clock() - start
# elapsed = timedelta(seconds=elapsed)
# print(elapsed)

# r = requests.get("https://www.baojia.com")
r = requests.get("http://127.0.0.1:8000/")

print(r.elapsed.total_seconds())
print(r.elapsed.seconds)
print(r.elapsed)
print(r.elapsed.microseconds / (1000 * 1000))

# help(r.elapsed)
