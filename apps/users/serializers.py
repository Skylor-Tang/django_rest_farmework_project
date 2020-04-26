# -*- coding: utf-8 -*-
# @Time    : 2020/4/26 15:29
# @Author  : Skylor Tang
# @Email   : 
# @File    : serializers.py
# @Software: PyCharm
import re
from datetime import datetime, timedelta

from rest_framework import serializers
from django.contrib.auth import get_user_model

from MxShop.settings import REGEX_MOBILE
from .models import VerifyCode

User = get_user_model()


class SmsSializers(serializers.Serializer):
    """ 因为只需要验证mobile字段，所以采用了普通的serializer """
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        """
        自定义验证函数，命名构成为validate_需要验证的字段名
        :param mobile:
        :return:
        """

        # 手机是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户名已经存在")

        # 验证手机号码是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")

        # 验证发送频率
        one_minutes_age = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_minutes_age, mobile=mobile).count():
            raise serializers.ValidationError("距离上次发送未超过60s")

        return mobile  # 注意，这里一定要返回验证的字段，否则在调用mobile = serializer.validated_data["mobile"]的时候没有值