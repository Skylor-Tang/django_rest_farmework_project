# -*- coding: utf-8 -*-
# @Time    : 2020/4/29 21:50
# @Author  : Skylor Tang
# @Email   : 
# @File    : permissions.py
# @Software: PyCharm

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:   # 对安全的请求方法，直接返回
            return True

        # Instance must have an attribute named `owner`.
        return obj.user == request.user
        # 对于不是安全的操作，要进行验证，验证的内容是可以随意设置的，要求返回bool值
        # 这里验证的是 操作的数据对象的user属性是否等于当前登录的用户
        # obj是数据表model的实例对象
