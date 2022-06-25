# -*- coding: utf8 -*-
'''
@Author : huangrenwu
@File: insert_account.py
@Time: 2022/6/24 11:20
@Email: leo.r.huang@microcore.tech
@Desc: 
'''

import xlrd2,redis,json

pika = redis.Redis(host='47.108.199.19',port=8379,password='spider666.',db=4)

xlsx_file = xlrd2.open_workbook('C:/Users/huangrenwu/Desktop/account.xlsx')
sheetOne = xlsx_file.sheets()[0]
for x in range(1,sheetOne.nrows):
    account = sheetOne.cell(x,4).value
    item = {
        "account": account,
        "passwd": "KF123456"
    }
    print(item)
    pika.lpush('yc_account_score',json.dumps(item))