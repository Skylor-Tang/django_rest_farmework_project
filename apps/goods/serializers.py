# -*- coding: utf-8 -*-
# @Time    : 2020/4/15 11:25
# @Author  : Skylor Tang
# @Email   : 
# @File    : serializers.py
# @Software: PyCharm

from rest_framework import serializers

from .models import Goods, GoodsCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class GoodSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Goods
        fields = "__all__"

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Goods.objects.create(**validated_data)

