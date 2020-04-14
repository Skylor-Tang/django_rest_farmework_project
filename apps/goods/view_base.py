# -*- coding: utf-8 -*-
# @Time    : 2020/4/14 22:34
# @Author  : Skylor Tang
# @Email   : 
# @File    : view_base.py
# @Software: PyCharm

from django.views.generic.base import View
from goods.models import Goods


class GoodsListView(View):
    def get(self, request, *args, **kwargs):
        json_list = []
        goods = Goods.objects.all()[:10]
        for good in goods:
            json_dict = {}
            json_dict['name'] = good.name
            json_dict['category'] = good.category.name  # 可以直接通过外键对象调用外键对象的属性。
            json_dict['market_price'] = good.market_price
            json_list.append(json_dict)

        from django.http import HttpResponse
        import json
        return HttpResponse(json.dumps(json_list), content_type="application/json" )
