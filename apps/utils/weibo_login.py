# -*- coding: utf-8 -*-
# @Time    : 2020/5/19 15:43
# @Author  : Skylor Tang
# @Email   : 
# @File    : weibo_login.py
# @Software: PyCharm


def get_auth_url():
    # 请求用户授权
    weibo_auth_url = 'https://api.weibo.com/oauth2/authorize'
    redirect_url = 'http://39.106.84.56:8001/complete/weibo/'  # 授权回调地址
    auth_url = weibo_auth_url + "?client_id={client_id}&redirect_uri={redirect_url}".format(
        client_id=2011318855, redirect_url=redirect_url
    )

    print(auth_url)


def get_access_token(code='589446ae85f00446ac231860aaa525c2'):
    # 获取授权后的Token
    access_token_url = "https://api.weibo.com/oauth2/access_token"
    import requests  # 需要使用post请求
    re_dict = requests.post(access_token_url, data={
        "client_id": 2011318855,
        "client_secret": "405ae53b8fc2703a52770f985e9035aa",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://39.106.84.56:8001/complete/weibo/"
    })


def get_user_info(access_token, uid):
    user_url = "https://api.weibo.com/2/users/show.json?access_token={token}&uid={uid}".format(
        token=access_token,
        uid=uid
    )
    print(user_url)


if __name__ == '__main__':
    get_auth_url()
    get_access_token()
    get_user_info('2.00Jhk8HEhuRHMCe367456d2fiBiLkB', 3774580035)
