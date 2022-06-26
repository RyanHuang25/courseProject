# -*- coding: utf8 -*-
'''
@Author: huangrenwu
@File: copy_account.py
@Time: 2022/6/26 21:14
@Email: leo.r.huang@microcore.tech
'''

import redis,json

pika = redis.Redis(host='47.108.199.19',port=8379,password='spider666.',db=4)

data_list = pika.lrange('yc_account_score',0,-1)
for data in data_list:
    data = json.loads(data)
    pika.lpush('yc_account',json.dumps(data))

