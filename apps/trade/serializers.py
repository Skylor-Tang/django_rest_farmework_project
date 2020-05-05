# -*- coding: utf-8 -*-
# @Time    : 2020/5/4 19:56
# @Author  : Skylor Tang
# @Email   : 
# @File    : serializers.py
# @Software: PyCharm


from rest_framework import serializers

from goods.models import Goods
from .models import ShoppingCart
from goods.serializers import GoodsSerializer


class ShopCartDetailSerializer(serializers.ModelSerializer):
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
