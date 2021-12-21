# Created by BaiJiFeiLong@gmail.com at 2021/12/20 16:08
import json

import mimesis
import redis

rds = redis.Redis()
rds.flushdb()

personMime = mimesis.Person(seed=0)
foodMime = mimesis.Food(personMime.seed)
addressMime = mimesis.Address(personMime.seed)
hardwareMime = mimesis.Hardware(personMime.seed)

for index in range(10):
    person = dict(
        fullname=personMime.full_name(),
        gender=personMime.gender(),
        age=personMime.age(),
        height=personMime.height(),
        weight=personMime.weight(),
        occupation=personMime.occupation(),
        email=personMime.email(),
    )
    address = dict(
        country=addressMime.country(True),
        province=addressMime.province(),
        region=addressMime.region(),
        street=addressMime.street_name(),
        postal=addressMime.postal_code()
    )
    computer = dict(
        cpu="{} {} {}".format(hardwareMime.cpu(), hardwareMime.cpu_model_code(), hardwareMime.cpu_frequency()),
        disk=hardwareMime.ssd_or_hdd(),
        graphics=hardwareMime.graphics(),
    )
    rds.set(f"PERSONS:{index + 1}", json.dumps(person))
    rds.set(f"PERSONS:{index + 1}:ADDRESS", json.dumps(address))
    rds.set(f"PERSONS:{index + 1}:COMPUTER", json.dumps(computer))

for index in range(10):
    rds.set(f"FOODS:DISHES:{index + 1}", foodMime.dish())
    rds.set(f"FOODS:FRUITS:{index + 1}", foodMime.fruit())
    rds.set(f"FOODS:VEGETABLES:{index + 1}", foodMime.vegetable())

for key in sorted(rds.keys()):
    print(key, rds.get(key))
