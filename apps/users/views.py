from django.shortcuts import render

# Create your views here.
from random import choice

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer
from utils.yunpian import YunPian
from MxShop.settings import API_KEY
from .models import VerifyCode

User = get_user_model()


class CustomBackend(ModelBackend):
    """
        自定义用户验证
    """

    # 重写ModelBackend的authenticate方法，添加用户手机验证
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            # 传递过来的password是明文，Django数据库中保存的是密文，check_password()会先加密再进行比对
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成四位数字验证码
        :return:
        """
        seeds = "1234567890"  # 种子
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        # 重写create方法，覆盖掉CreateModelMixin中的create()方法
        serializer = self.get_serializer(data=request.data)
        # 设置为True之后，在此处出现异常的时候就会直接抛出异常而不继续执行
        # 抛出异常的时候会被drf捕捉到，返回400
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]

        yunpian = YunPian(API_KEY)
        code = self.generate_code()
        sms_status = yunpian.send_sms(code=code, mobile=mobile)

        # 返回字段数据提取
        if sms_status["code"] != 0:
            return Response({
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 验证码记录保存
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)  # create 返回的状态码就是201


class UserViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户数据相关
    """
    # serializer_class = UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

    def get_serializer_class(self):
        """
        重写get_serializer_class方法，完成serializer的动态获取
        :return:
        """
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer

        return UserDetailSerializer

    def get_permissions(self):
        """
        重写get_permissions方法，完成动态权限给予功能
        :return:
        """
        # self的action属性，只有使用ViewSet方法才有
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []

        return []  # 这步骤不能少，if条件之外的也要有返回值

    def create(self, request, *args, **kwargs):
        """
        为了完成配合前端实现的 注册完成后即自动登录的要求
        重载create方法，完成token的返回
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 重载perform_create方法，使其返回创建的实例对象，这里获取到该返回值
        user = self.perform_create(serializer)
        re_dict = serializer.data

        # 分析jwt源码，调用源码组件，完成token的构建
        payload = jwt_payload_handler(user)
        # 获取返回的对象serializer.data，并添加token字段，由前端获取到
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username
        headers = self.get_success_headers(serializer.data)

        # 返回修改后的值
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        # 此处限定了，无论访问什么pk，都是返回的当前的
        return self.request.user

    def perform_create(self, serializer):
        """
        重载该方法，使其返回存储的对象
        该函数原先只是调用了函数，但是没有返回
        drf内实现的save()方法默认是返回了当前创建的实例对象的
        :param serializer:
        :return:
        """
        return serializer.save()
