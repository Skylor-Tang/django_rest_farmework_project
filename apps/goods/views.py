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

    def post(self, request, format=None):
        '''
        本项目中，多是取数据的操作，用户的上传操作都是通过后台完成，所以post用的少
        :param request:
        :param format:
        :return:
        '''
        # 下面使用的request.data中的request是重载过的，所有有data属性
        serializer = GoodSerializer(data=request.data)
        if serializer.is_valid():
            # 执行save时，会调用serializers中定义的create方法
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
