# -*- coding: utf-8 -*-
# @Time    : 2020/4/15 11:25
# @Author  : Skylor Tang
# @Email   : 
# @File    : serializers.py
# @Software: PyCharm

from rest_framework import serializers
from django.db.models import Q

from .models import Goods, GoodsCategory, HotSearchWords, GoodsImage, Banner, GoodsCategoryBrand, IndexAd


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


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class GoodsCategoryBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


class IndexCategorySerializer(serializers.ModelSerializer):
    brands = GoodsCategoryBrandSerializer(many=True)
    goods = serializers.SerializerMethodField()
    sub_cat = CategorySerializer2(many=True)
    ad_goods = serializers.SerializerMethodField()

    def get_ad_goods(self, obj):
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            good_ins = ad_goods[0].goods
            goods_json = GoodsSerializer(good_ins, many=False, context={'request': self.context["request"]}).data
        return goods_json

    def get_goods(self, obj):
        """
        命名必须采用 get_字段名 的方式
        此处的obj参数为当前model指定的类的实例对象
        :param obj:
        :return:
        """
        all_goods = Goods.objects.filter(Q(category_id=obj.id) | Q(category__parent_category_id=obj.id)
                                         | Q(category__parent_category__parent_category_id=obj.id))
        # 传递QuerySet类型数据，使用serializer类接收，得到serializer的实例话对象，验证后的值存放在data属性中
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context["request"]})
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = "__all__"
