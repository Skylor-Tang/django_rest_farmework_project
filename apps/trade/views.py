import time

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins

from utils.permissions import IsOwnerOrReadOnly
from .serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from .models import ShoppingCart, OrderInfo, OrderGoods


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    购物车功能
    list:
        获取购物车详情
    create:
        加入购物车
    delete:
        删除购物车物品
    update:
        更新记录
    """
    serializer_class = ShopCartSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    lookup_field = "goods_id"  # 使用商品作为查询字段

    def perform_create(self, serializer):
        # 重写，购置商品的时候减少库存
        shop_cart = serializer.save()
        goods = shop_cart.goods
        goods.goods_num -= shop_cart.nums
        goods.save()

    def perform_destroy(self, instance):
        # 重写， 删除购物车中的商品的时候返还库存
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()  # 这里注意操作顺序，删除放在最后，因为需要用到删除的数据

    def perform_update(self, serializer):
        # 重写， 修改数量的时候，动态改变库存数
        existed_record = ShoppingCart.objects.get(id=serializer.instance.id)
        existed_nums = existed_record.nums
        saved_record = serializer.save()
        nums = saved_record.nums - existed_record.nums
        goods = saved_record.goods
        goods.goods_num -= nums
        goods.save()

    def get_serializer_class(self):
        if self.action == "list":
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)


class OrderViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    订单管理（不允许修改）
    list:
        获取个人订单
    delete:
        删除订单
    create:
        新增订单
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

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
