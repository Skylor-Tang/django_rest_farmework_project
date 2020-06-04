# django_rest_farmework_project
使用 Django_rust_farmework 和 vue 实现的前后端分离的商城项目

项目内容：使用前后端分离的开发模式，借助Django REST framework完成网站api的开发，配合前端vue实现网站功能。

+ 权限
  + Authentication用户认证设置
  + 动态设置Permission、Authentication
  + Validators实现字段验证
+ 登录
  + 使用OAuth2，实现微博第三方登录。
  + 使用第三方发送手机验证码，实现手机注册登录。
  + Django实现JWT的验证登录功能
+ 缓存
  + 使用Redis实现Django REST framework的缓存、Throttling对用户和IP进行限速
+ 支付
  + 对接支付宝，实现手机支付功能
+ 文档
  + 接口文档自动化管理 
