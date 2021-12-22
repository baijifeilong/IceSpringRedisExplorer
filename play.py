# Created by BaiJiFeiLong@gmail.com at 2021/12/20 16:08
import json

import mimesis
import redis

rds0 = redis.Redis()
rds1 = redis.Redis(db=1)
rds2 = redis.Redis(db=2)
rds0.flushall()

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
    rds0.set(f"PERSONS:{index + 1}", json.dumps(person))
    rds0.set(f"PERSONS:{index + 1}:ADDRESS", json.dumps(address))
    rds0.set(f"PERSONS:{index + 1}:COMPUTER", json.dumps(json.dumps(computer)))

for index in range(10):
    rds0.set(f"FOODS:DISHES:{index + 1}", foodMime.dish())
    rds1.set(f"FOODS:FRUITS:{index + 1}", foodMime.fruit())
    rds2.set(f"FOODS:VEGETABLES:{index + 1}", foodMime.vegetable())
