# -*- coding: utf-8 -*-
# @Time    : 2020/4/15 11:25
# @Author  : Skylor Tang
# @Email   : 
# @File    : serializers.py
# @Software: PyCharm

from rest_framework import serializers

from .models import Goods, GoodsCategory, HotSearchWords, GoodsImage


class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    sub_cat = CategorySerializer2(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ("image",)


class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    images = GoodsImageSerializer(many=True)

    class Meta:
        model = Goods
        fields = "__all__"

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.

        create 方法只会在 执行 save方法的时候调用
        实例对象调用save方法完成数据存储的时候，调用的是create方法
        """
        return Goods.objects.create(**validated_data)


class HotWordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotSearchWords
        fields = "__all__"

