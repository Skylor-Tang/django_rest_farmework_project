from rest_framework.response import Response
from rest_framework import mixins, generics
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

from .models import Goods
from .serializers import GoodsSerializer


class GoodsPagination(PageNumberPagination):
    ''' 使用自定义的分页类，会覆盖掉setting中PAGINATION的相关配置'''
    page_size = 5
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 100  # 页面内最大数据量，用来限制pagepage_size_query_param设置的上限


class GoodslistView(generics.ListAPIView):
    """
    商品列表页
    """
    queryset = Goods.objects.all()[:10]
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination

