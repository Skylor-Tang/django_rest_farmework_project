# -*- coding: utf-8 -*-
# @Time    : 2020/4/16 10:44
# @Author  : Skylor Tang
# @Email   : 
# @File    : filters.py
# @Software: PyCharm

import django_filters
from django.db.models import Q

from .models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    """
    自定义过滤器，实现区间过滤
    """
    pricemin = django_filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    pricemax = django_filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    top_category = django_filters.NumberFilter(field_name="category_id", method='top_category_filter')

    def top_category_filter(self, queryset, name, value):
        return queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value)
                               | Q(category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ['pricemin', 'pricemax', 'top_category']