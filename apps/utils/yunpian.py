# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 15:02
# @Author  : Skylor Tang
# @Email   : 
# @File    : yunpian.py
# @Software: PyCharm

import requests
import json


class YunPian:
    def __init__(self, api_key):
        self.api_key = api_key
        self.single_send_url = "https://sms.yunpian.com/v2/sms/single_send.json"

    def send_sms(self, code, mobile):
        parmas = {
            "apikey": self.api_key,
            "mobile": mobile,
            "text": "【唐美健】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }
        response = requests.post(self.single_send_url, data=parmas)
        re_dict = json.loads(response.text)
        return re_dict


if __name__ == '__main__':
    yun_pian = YunPian("2269abf14879c7fc226204d1f734a27f")
    print(yun_pian.send_sms("1117", "18262875767"))
