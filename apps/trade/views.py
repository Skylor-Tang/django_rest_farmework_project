import time

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect

from utils.permissions import IsOwnerOrReadOnly
from .serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from .models import ShoppingCart, OrderInfo, OrderGoods
from utils.alipay import AliPay
from MxShop.settings import app_private_key_path, alipay_public_key_path
import datetime


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


class OrderViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
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
        完成购物车数据清除，直接在后台完成数据的清楚，前端在跳转购物车页面的时候会再次请求，此时没有数据了就完成了清空
        并完成购物车数据像详情订单表中的转移
        :param serializer:
        :return:
        """
        order = serializer.save()
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            # 手动为订单详情表添加数据
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()

            shop_carts.delete()  # 数据转移完成，删除购物车中的数据
        return order


class AliPayView(APIView):
    def get(self, request):
        """
        处理支付宝的return_url返回
        :param request:
        :return:
        """
        # 做签名验证，验证支付宝返回的消息的正确性
        process_dict = {}
        for key, value in request.GET.items():
            process_dict[key] = value
        sign = process_dict.pop("sign")

        alipay = AliPay(
            appid="2016102100732808",
            app_notify_url="http://39.106.84.56:8001/alipay/return/",
            app_private_key_path=app_private_key_path,  # 在settings.py中配置路径，使用相对路径
            alipay_public_key_path=alipay_public_key_path,
            debug=True,  # 默认False,
            return_url="http://39.106.84.56:8001/alipay/return/"
        )
        verify_re = alipay.custom_verify(process_dict, sign)

        if verify_re is True:
            order_sn = process_dict.get('out_trad_no', None)
            trade_no = process_dict.get('trade_no', None)
            trade_status = process_dict.get('trade_status', None)

            # 查询到相应的订单，修改订单的状态以及信息
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.datetime.now()
                existed_order.save()

            # 向支付宝返回success消息，否则支付宝会一直发送 支付成功 的消息
            # return Response("success")
            response = redirect("index")  # 使用 url的命名直接跳转到相应的url下
            response.set_cookie("nextPath", "pay", max_age=2)
            return response
        else:
            response = redirect("index")
            return response

    def post(self, request):
        """
        处理支付宝的notify_url返回
        :param request:
        :return:
        """
        # 做签名验证，验证支付宝返回的消息的正确性
        process_dict = {}
        for key, value in request.POST.items():
            process_dict[key] = value
        sign = process_dict.pop("sign")

        alipay = AliPay(
            appid="2016102100732808",
            app_notify_url="http://39.106.84.56:8001/alipay/return/",
            app_private_key_path=app_private_key_path,  # 在settings.py中配置路径，使用相对路径
            alipay_public_key_path=alipay_public_key_path,
            debug=True,  # 默认False,
            return_url="http://39.106.84.56:8001/alipay/return/"
        )
        verify_re = alipay.custom_verify(process_dict, sign)

        if verify_re is True:
            order_sn = process_dict.get('out_trad_no', None)
            trade_no = process_dict.get('trade_no', None)
            trade_status = process_dict.get('trade_status', None)

            # 查询到相应的订单，修改订单的状态以及信息
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.datetime.now()
                existed_order.save()

            # 向支付宝返回success消息，否则支付宝会一直发送 支付成功 的消息
            return Response("success")
