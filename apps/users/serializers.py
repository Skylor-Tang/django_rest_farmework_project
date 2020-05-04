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
from rest_framework.validators import UniqueValidator

from MxShop.settings import REGEX_MOBILE
from .models import VerifyCode

User = get_user_model()


class SmsSerializer(serializers.Serializer):
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


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类（返回用）
    """

    class Meta:
        model = User
        fields = ("name", "gender", "birthday", "email", "mobile")


class UserRegSerializer(serializers.ModelSerializer):
    # code为多余的字段，只做验证，后面去除
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")

    username = serializers.CharField(required=True, allow_blank=False, label="用户名",
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    password = serializers.CharField(
        style={'input_type': 'password'},  # 设置密码为密文显示
        label="密码", write_only=True,
    )

    def create(self, validated_data):
        """
        Serializer调用save()方法的时候实际上会调用create()方法完成model实例的创建
        内部还是重新调用了原先的create方法，然后重新对密码进行了django自带的密文加密方式加密后保存
        因为这里的用户保存，只是单纯的用户存储，使用的不是密文加密方式。
        :param validated_data:
        :return:
        """
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate_code(self, code):
        # try:
        #     verify_records = VerifyCode.objects.get(mobile=self.initial_data["username"], code=code)
        # except VerifyCode.DoesNotExist as e:
        #     pass
        # except VerifyCode.MultipleObjectsReturned as e:
        #     pass
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        # self.initial_data["username"]方法用于获得前端传递过来的post属性值
        if verify_records:
            last_records = verify_records[0]

            five_minutes_age = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_minutes_age > last_records.add_time:
                raise serializers.ValidationError("验证码过期")

            if last_records.code != code:
                raise serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码错误")

        # 该方法之后是没有使用 return code 进行返回，所以，使用实例化对象调用 .validated_data["code"]的时候，得到的值是None
        # 一般的该方法是需要返回字段值的，但是由于这里只需要验证的功能，后面也不需要使用到code（设置了为write_only=True），所以没有做返回

    def validate(self, attrs):
        """
        作用于所有的字段验证上，做一些统一的处理
        :param attrs: 是每个字段单独validate之后返回的数据集
        :return:
        """
        attrs["mobile"] = attrs["username"]
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile",
                  "password")  # User表中没有code字段，这里添加是为了方便验证,当然也是必须要添加了，因为所有serializer中设置的字段都必须出现在fields中
