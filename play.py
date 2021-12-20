# Created by BaiJiFeiLong@gmail.com at 2021/12/20 16:08
import json

import mimesis
import redis

generic = mimesis.Generic(seed=0)

rds = redis.Redis()

personMime = mimesis.Person(seed=0)
foodMime = mimesis.Food(seed=0)

for index in range(10):
    person = dict(
        fullname=personMime.full_name(),
        gender=personMime.gender(),
        age=personMime.age(),
        height=personMime.height(),
        weight=personMime.weight()
    )
    rds.set(f"PERSONS:{index + 1}", json.dumps(person))

for index in range(10):
    rds.set(f"DISHES:{index + 1}", foodMime.dish())

for key in rds.keys():
    print(key, rds.get(key))
