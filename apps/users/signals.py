# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 17:57
# @Author  : Skylor Tang
# @Email   : 
# @File    : signals.py
# @Software: PyCharm

# 使用信号量机制完成密码加密的操作
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user(sender, instance=None, created=False, **kwargs):
    if created:
        password = instance.password
        instance.set_password(password)
        instance.save()