from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Goods
from .serializers import GoodSerializer


class GoodslistView(APIView):
    """
    list all goods
    """
    def get(self, request, format=None):
        goods = Goods.objects.all()[:10]
        # 当序列化的对象是列表的时候，需要指定many参数，意思是序列化为数组
        good_serializer = GoodSerializer(goods, many=True)
        # 使用.data获得序列化之后的数据
        return Response(good_serializer.data)
