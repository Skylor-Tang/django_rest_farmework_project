"""MxShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path, include
from django.views.static import serve

import xadmin
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token

from MxShop.settings import MEDIA_ROOT
from goods.views import GoodsListViewSet, CategoryViewSet, BannerViewSet, IndexCategoryViewSet
from users.views import SmsCodeViewset, UserViewSet
from trade.views import ShoppingCartViewSet, OrderViewSet
from user_operation.views import UserFavViewSet, LeavingMessageViewSet, AddressViewSet
from django.views.generic import TemplateView
from trade.views import AliPayView


router = DefaultRouter()
# 配置goods的URL
router.register(r'goods', GoodsListViewSet, basename='goods')  # 未设置basename的时候，将采用默认的设置，这里d的默认值是goods-list

# 配置category的url
router.register(r'categorys', CategoryViewSet, basename='categorys')

# 配置smscode的url
router.register(r'codes', SmsCodeViewset, basename='codes')

# 配置users注册的url
router.register(r'users', UserViewSet, basename='users')

# 配置userfav的rul
router.register(r'userfavs', UserFavViewSet, basename="userfavs")

# 留言
router.register(r'messages', LeavingMessageViewSet, basename='messages')

# 收货地址
router.register(r'address', AddressViewSet, basename='address')

# 购物车
router.register(r'shopcarts', ShoppingCartViewSet, basename='shopcarts')

# 个人订单
router.register(r'orders', OrderViewSet, basename='orders')

# 轮播图
router.register(r'banners', BannerViewSet, basename='banners')

# 首页商品系列类数据
router.register(r'indexgoods', IndexCategoryViewSet, basename='indexgoods')

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # drf自带的认证模式 post请求
    url(r'^api-token-auth/', views.obtain_auth_token),
    # djangorestframework-jwt的jwt认证接口 post请求
    url(r'^login/$', obtain_jwt_token),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

    url(r'^', include(router.urls)),
    url(r'docs/', include_docs_urls(title='生鲜网站')),

    # 第三方登录 social_django 配置
    url('', include('social_django.urls', namespace='social')),

    # vue 前端首页跳转
    url(r'^index/', TemplateView.as_view(template_name="index.html"), name="index"),

    # 手动配置，支付宝支付访问的url
    url(r'^alipay/return/', AliPayView.as_view(), name="alipay"),

]
