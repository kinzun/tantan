from urllib.parse import quote, unquote, unquote_plus, quote_plus


b = "http://me.baojia.com/bike/search/adCode?latitude=39&longitude=116"
print(quote_plus(b))
s = unquote_plus(b)
print(s)
print(quote_plus(s))

import random
from retrying import retry


@retry(stop_max_attempt_number=3)
def do_something_unreliable():
    if random.randint(0, 10) > 1:
        print('g')
        # raise IOError("Broken sauce, everything is hosed!!!111one")
        raise KeyError('kk')
    else:
        return "Awesome sauce!"


print(do_something_unreliable())
