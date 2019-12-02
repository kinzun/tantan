a = list(range(10))

dict_li = {"par": a}


def te(*args, **kwargs):
    print(*args)
    print(kwargs)


_s = [{'test1': '1'}, {'test2': '2'}]

for i in _s:
    i.update({'yaxisside': 1})

    print(_s)
