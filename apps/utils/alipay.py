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

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


if __name__ == "__main__":
    return_url = 'http://47.92.87.172:8000/?total_amount=0.01&timestamp=2017-08-15+17%3A15%3A13&sign=jnnA1dGO2iu2ltMpxrF4MBKE20Akyn%2FLdYrFDkQ6ckY3Qz24P3DTxIvt%2BBTnR6nRk%2BPAiLjdS4sa%2BC9JomsdNGlrc2Flg6v6qtNzTWI%2FEM5WL0Ver9OqIJSTwamxT6dW9uYF5sc2Ivk1fHYvPuMfysd90lOAP%2FdwnCA12VoiHnflsLBAsdhJazbvquFP%2Bs1QWts29C2%2BXEtIlHxNgIgt3gHXpnYgsidHqfUYwZkasiDGAJt0EgkJ17Dzcljhzccb1oYPSbt%2FS5lnf9IMi%2BN0ZYo9%2FDa2HfvR6HG3WW1K%2FlJfdbLMBk4owomyu0sMY1l%2Fj0iTJniW%2BH4ftIfMOtADHA%3D%3D&trade_no=2017081521001004340200204114&sign_type=RSA2&auth_app_id=2016080600180695&charset=utf-8&seller_id=2088102170208070&method=alipay.trade.page.pay.return&app_id=2016080600180695&out_trade_no=201702021222&version=1.0'

    alipay = AliPay(
        appid="2016102100732808",
        app_notify_url="http://projectsedus.com/",
        app_private_key_path="../trade/keys/private_2048.txt",  # 个人私钥
        alipay_public_key_path="../trade/keys/alipay_key_2048.txt",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=True,  # 默认False,
        return_url="http://39.106.84.56:8001/"
    )

    o = urlparse(return_url)
    query = parse_qs(o.query)
    processed_query = {}
    ali_sign = query.pop("sign")[0]
    for key, value in query.items():
        processed_query[key] = value[0]
    print(alipay.verify(processed_query, ali_sign))

    url = alipay.direct_pay(
        # 订单信息描述  该函数执行后，生成整个请求的完整字符串
        subject="测试订单",
        out_trade_no="202002021234",  # 订单号
        total_amount=1.1,  # 订单总额
        return_url="http://39.106.84.56:8001/"  # 提供 付款完成之后的回调页面
    )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(
        data=url)  # 使用direct_pay返回的url，构建完整的访问路径，此处使用的接口为沙箱接口
    print(re_url)
