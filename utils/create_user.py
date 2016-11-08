# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# Date: 2016-10-03
# auth: nevermore

import requests
from django.conf import settings


def create_company_and_user_ops_level3(*args, operations=True):
    '''
    company_name, company_alias, owner_name, owner_email, domains
    company_name: 公司全称
    company_alias: 公司简写 用于ops内部快捷登录
    owner_name: 用户昵称
    owner_email: 用户邮箱
    domains: 需要输入一个list，ex:["testc.com", "..."...]
    defuatl operations:True accept boolen only
    '''
    create_company_url = settings.TAN14_API_BASE_URL + 'useful/create/company'
    company_name, company_alias, owner_name, owner_email, domains = args
    data = {"company_name": company_name,
            "company_alias": company_alias,
            "owner_name": owner_name,
            "owner_email": owner_email}
    resp = requests.post(create_company_url, data=data)
    if resp.status_code > 399:
        print(create_company_url, data)
        print('Got error with create ops company owner:\n')
        print(resp.text)
        return
    info = resp.json()
    print('Created user on mcaccount:', info)
    data = {"login_email": owner_email, 'operations': operations}
    level3_user_url = settings.TAN14_API_BASE_URL + 'level3/user'
    resp = requests.post(level3_user_url, data=data)
    if resp.status_code > 399:
        print(level3_user_url, data)
        print('Got error with create level3 user:\n')
        print(resp.text)
        return
    user_domains_url = settings.TAN14_API_BASE_URL + 'level3/user_domains'
    data = {"login_email": owner_email, "cdn": "level3", "domains": domains}
    resp = requests.post(user_domains_url, data=data)
    if resp.status_code > 399:
        print('Got error with map level3 user domains:\n')
        print(user_domains_url, data)
        print(resp.text)
    else:
        print({u'帐号': owner_name,
               u'密码': info.get('login_passwd'),
               u'公司名称': company_name})



