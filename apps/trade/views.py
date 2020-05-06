import time

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins

from utils.permissions import IsOwnerOrReadOnly
from .serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer
from .models import ShoppingCart, OrderInfo, OrderGoods


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    create:
        加入购物车
    delete:
        删除购物记录
    update:
        更新记录
    """
    serializer_class = ShopCartSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    lookup_field = "goods_id"  # 使用商品作为查询字段

    def get_serializer_class(self):
        if self.action == "list":
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


class OrderViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    订单管理（不允许修改）
    list:
        获取个人订单
    delete:
        删除订单
    create:
        新增订单
    """
    serializer_class = OrderSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        完成购物车数据清楚，直接在后台完成数据的清楚，前端在跳转购物车页面的时候会再次请求，此时没有数据了就完成了清空
        并完成购物车数据像详情订单表中的转移
        :param serializer:
        :return:
        """
        order = serializer.save()
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_carts in shop_carts:
            # 手动为订单详情表添加数据
            order_goods = OrderGoods()
            order_goods.goods = shop_carts.goods
            order_goods.goods_num = shop_carts.nums
            order_goods.order = order
            order_goods.save()

            shop_carts.delete()  # 数据转移完成，删除购物车中的数据
        return order
