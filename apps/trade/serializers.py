# -*- coding: utf-8 -*-
# @Time    : 2020/5/4 19:56
# @Author  : Skylor Tang
# @Email   : 
# @File    : serializers.py
# @Software: PyCharm
import time

from rest_framework import serializers

from goods.models import Goods
from .models import ShoppingCart, OrderInfo, OrderGoods
from goods.serializers import GoodsSerializer


class ShopCartDetailSerializer(serializers.ModelSerializer):
    """
    专用于显示
    """
    goods = GoodsSerializer(many=False)

    class Meta:
        model = ShoppingCart
        fields = "__all__"


class ShopCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, min_value=1,
                                    label="购买数量",
                                    help_text="购买数量",
                                    error_messages={
                                        "min_value": "商品数量不能小于一",
                                        "required": "请选择购买数量"
                                    })
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all(), label="商品", help_text="商品")

    def create(self, validated_data):
        """
        serializers.Serializer中，该接口需要手动实现
        :param validated_data:
        :return:
        """
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]
        # goods得到的是goods的一条数据的实例对象，但是在使用的时候，前端api中传递的是goods_id的数值
        # serializer在得到数据之后处理的时候，因为是外键对象，所以使用该数据的时候会自动转换为找到的实例对象

        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    def update(self, instance, validated_data):
        """
        修改商品数量
        serializers.Serializer中，该接口需要手动实现
        :param instance:
        :param validated_data:
        :return:
        """
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 以下三个字段，设置为只读，不能设置，需要在支付完成之后才能修改
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)

    def generate_order_sn(self):
        """
        用于订单号的生成
        生成方式： 当前时间+userid+随机数
        :return:
        """
        from random import Random
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context["request"].user.id,
                                                       ranstr=random_ins.randint(10, 99))
        return order_sn

    def validate(self, attrs):
        """
        添加订单号参数
        :param attrs:
        :return:
        """
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = "__all__"
