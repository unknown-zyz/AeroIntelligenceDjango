import jwt
from django.http import JsonResponse
from Tools.MakeToken import JWT_TOKEN_KEY
from User.models import User
from channels.db import database_sync_to_async
from functools import wraps
from rest_framework.response import Response
from Tools.MakeToken import JWT_TOKEN_KEY


def login_required(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return Response({'error': 'Token is missing'}, status=401)
        try:
            payload = jwt.decode(token, JWT_TOKEN_KEY, algorithms=['HS256'])
            uid = payload['uid']
            user = User.objects.get(pk=uid)
            request.user = user
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=401)
        return view_func(self, request, *args, **kwargs)
    return wrapper


# def loginCheck(func):
#     def wrap(request, *args, **kwargs):
#         token = request.META.get('HTTP_AUTHORIZATION')
#         if not token:
#             return JsonResponse({'code': 400, 'message': "请重新登录", 'data': {}})
#         try:
#             res = jwt.decode(token, JWT_TOKEN_KEY, algorithms='HS256')
#         except Exception as e:
#             print('jwt decode error is %s' % e)
#             return JsonResponse({'code': 400, 'message': "请重新登录", 'data': {}})
#
#         uid = res['uid']
#         if uid < 1000000:
#             user = User.objects.get(uid=uid)
#             request.myUser = user
#         return func(request, *args, **kwargs)
#     return wrap


# def asyncLoginCheck(func):
#     async def wrap(request,*args,**kwargs):
#         token = request.META.get('HTTP_AUTHORIZATION')
#         if not token:
#             return JsonResponse({'code': 400, 'message': "请重新登录", 'data': {}})
#         try:
#             res = jwt.decode(token,JWT_TOKEN_KEY,algorithms='HS256')
#         except Exception as e:
#             print('jwt decode error is %s'%e)
#             return JsonResponse({'code': 400, 'message': "请重新登录", 'data': {}})
#
#         uid = res['uid']
#         user  = await get_user(uid)
#         request.myUser = user
#         response = await func(request, *args, **kwargs)  # 在这里使用 'await'
#
#         if response is None:
#             # 如果装饰的视图函数返回了None，返回一个适当的HttpResponse对象
#             return JsonResponse({'code': 500, 'message': "服务器错误", 'data': {}})
#         return response
#     return wrap

@database_sync_to_async
def get_user(uid):
    return User.objects.get(uid=uid)
