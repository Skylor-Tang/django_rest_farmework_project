# -*- coding: utf-8 -*-
# @Time    : 2020/5/21 11:16
# @Author  : Skylor Tang
# @Email   : 
# @File    : alipay.py
# @Software: PyCharm


from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json


class AliPay:
    """
    支付宝支付接口构造
    """

    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None  # 通过下面的读文件的形式，获得文件中的私钥
        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())  # 使用 RSA.import_key 对读取的私钥作加密

        # 公钥的读取，在生成连接的操作中没有用途
        # 但是在验证支付宝给我们返回的消息的时候，是最主要的key
        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())

        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"  # 若是测试环境，使用 沙箱提供的访问接口
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"  # 生产环境接口

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        """
        对外返回请求参数的主要接口
        :param subject:
        :param out_trade_no:
        :param total_amount:
        :param return_url:
        :param kwargs:
        :return:
        """
        biz_content = {  # 订单消息的参数 主要提供了4个必填的参数
            "subject": subject,  # 订单标题
            "out_trade_no": out_trade_no,  # 订单号
            "total_amount": total_amount,  # 订单金额
            "product_code": "FAST_INSTANT_TRADE_PAY",  # 销售产品码 为固定值
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)  # 当传递了额外参数的时候，负责接受 订单信息除了必填字段外还有别的字段
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)  # 调用 主体参数构成方法，传递biz_content参数
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        """
        接口主要的公共参数主体 根据文档说明构造
        :param method:
        :param biz_content:
        :param return_url:
        :return:
        """
        data = {
            "app_id": self.appid,
            "method": method,  # 接口名称
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        """
        商户请求参数（添加签名串）构造
        :param data:
        :return:
        """
        data.pop("sign", None)  # sign签名的时候不能含有sign字段，所以要取去除
        # 按照文档要求，对所有的请求参数按照第一个字符的键值ASCII码递增排序
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)  # 将排序好的列表值取出构建{0}={1}形式，并用等号连接
        sign = self.sign(unsigned_string.encode("utf-8"))  # 使用utf-8编码之后进行签名构造，返回构造好的签名
        # 和构造签名的时候不同，此处需要将传递的参数惊醒处理，包括空格的去除等等，但是之前构造签名时不需要进行这个操作
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)  # 将签名sign添加进去请求参数中
        return signed_string  # 最终返回的 请求url中的传递的参数

    def ordered_data(self, data):
        """
        对所有的请求参数按照第一个字符的键值ASCII码递增排序
        :param data:
        :return:
        """
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将传递的值是字典类型的数据进行处理（本身传递的参数是字典，这里操作的对象是值还是字典的数据，主要是指 biz_content 字段 ）
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))  # 将 biz_content 内的参数构建为json格式的字符串

        return sorted([(k, v) for k, v in data.items()])  # 返回排序好的参数的元组列表

    def sign(self, unsigned_string):
        """
        开始计算签名，使用官方文档要求的构建方式进行构建
        :param unsigned_string:
        :return:
        """
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))  # 利用商户私钥对待签名字符串进行签名
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _custom_verify(self, raw_content, signature):
        """
        签名计算以及验证
        :param raw_content: 计算签名的完整格式的参数
        :param signature:  返回的签名
        :return:
        """
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def custom_verify(self, data, signature):
        """
        验证支付宝付支付成功后的返回请求是否被篡改
        实际上是一个使用公钥验证签名是否被篡改的过程 根据官方文档要求进行构建 https://opendocs.alipay.com/open/200/106120
        :param data: 去除sign的返回值字典
        :param signature: 返回的签名
        :return:
        """
        if "sign_type" in data:
            sign_type = data.pop("sign_type")  # 去除参数中的签名类型，文档要求
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)  # 对剩余的参数进行排序
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)  # 构建请求参数
        return self._custom_verify(message, signature)  # 调用 _verify() 进行签名计算并验证是否一致。


# 订单号生成函数
def out_trade_no_func():
    from random import randint
    out_trade_no = "".join(str(randint(0, 9)) for i in range(13))
    return out_trade_no


if __name__ == "__main__":
    alipay = AliPay(
        appid="2016102100732808",
        app_notify_url="http://shop.skylor.top/alipay/return/",
        app_private_key_path="../trade/keys/private_2048.txt",  # 个人私钥
        alipay_public_key_path="../trade/keys/alipay_key_2048.txt",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=True,  # 默认False,
        return_url="http://shop.skylor.top/alipay/return/"
    )

    # 订单号生成

    url = alipay.direct_pay(
        # 订单信息描述  该函数执行后，生成整个请求的完整字符串
        subject="测试订单",
        out_trade_no=out_trade_no_func(),  # 订单号
        total_amount=1.1,  # 订单总额
        # return_url="http://shop.skylor.top/alipay/return/"  # 提供 付款完成之后的回调页面  省略，初始化时已经提供
    )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(
        data=url)  # 使用direct_pay返回的url，构建完整的访问路径，此处使用的接口为沙箱接口
    print(re_url)

    # 做回调验证
    return_url = 'http://shop.skylor.top/?charset=utf-8&out_trade_no=202002021235&method=alipay.trade.page.pay.return&total_amount=1.10&sign=LHHqGQljTRFpOu%2BCPCnA0OcClKFH3wOVuxpu2HAtXibbdx9gwR2R%2BDDJaKzQaZBWJ5DpPIgZs5Zh2vGo5neNKP4BYDhrD4YYLkumnX%2Be%2BlG53xvxb1TQMOZxKKjTDqWpwHvD25GPJh00K7WCvZ2anUuMRt4JdcxXpuyMqSIbGUMT81yccfeCGMZHrtOQvOreWP1WDs923UHabmke6cuw%2F4BEr8jhnO8e9Oe4WD7N%2B6u1e2aojQNB92QMOSlyeOGetJqVLEfuK9K8JJQ5wUCD%2BR%2FSAt7ml2kSxN1U9cgsJIDvMvmNC5skGbrtnCZx1239IZoYWDZGtEX1Rbj%2FxFqmZw%3D%3D&trade_no=2020052222001410920500926725&auth_app_id=2016102100732808&version=1.0&app_id=2016102100732808&sign_type=RSA2&seller_id=2088102180531500&timestamp=2020-05-22+10%3A33%3A49'

    # 以下两个方法，配合完成返回url中参数的获取
    o = urlparse(return_url)  # urlparse() 负责对返回的url进行解析，返回值的参数都在query属性中 返回值为ParseResult类型
    query = parse_qs(o.query)  # 调用对象的query属性，所有传递过来的参数都在该属性中，然后使用parse_qs()对属性进行获取，返回值的类型为dict，字典的值为列表类型
    processed_query = {}
    ali_sign = query.pop("sign")[0]  # 去除sign值（返回的签名），并保存该值用于签名的对比验证
    for key, value in query.items():
        processed_query[key] = value[0]  # 构建去除sign之后所有的参数的字典
    print(alipay.custom_verify(processed_query, ali_sign))  # 未被篡改，返回true，否则返回false

    print(out_trade_no_func())
