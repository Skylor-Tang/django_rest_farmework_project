# -*- coding: utf-8 -*-
# @Time    : 2020/4/16 10:44
# @Author  : Skylor Tang
# @Email   : 
# @File    : filters.py
# @Software: PyCharm


import django_filters
from .models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    自定义过滤器，实现区间过滤
    """
    price_min = django_filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Goods
        fields = ['price_min', 'price_max', 'name']