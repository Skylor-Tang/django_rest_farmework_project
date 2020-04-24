from django.shortcuts import render

# Create your views here.

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

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