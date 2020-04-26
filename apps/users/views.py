from django.shortcuts import render

# Create your views here.
from random import choice

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .serializers import SmsSializers
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


class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSializers

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
        # 重写create方法
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
            }, status=status.HTTP_201_CREATED)   # create 返回的状态码就是201
