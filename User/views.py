import json
import re

from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.http import JsonResponse

from Tools.MakeToken import make_token
from User.models import *


def userRegister(request):
    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj.get('phone')
    password = json_obj.get('password')
    confirm_password = json_obj.get('confirmPassword')
    if not re.match('^1\d{10}$', phone):
        return JsonResponse({'code': 400, 'message': "手机号不合法", 'data': {}})
    elif User.objects.filter(phone=phone).exists():
        return JsonResponse({'code': 400, 'message': "手机号已存在", 'data': {}})
    elif password != confirm_password:
        return JsonResponse({'code': 400, 'message': "两次密码不同", 'data': {}})
    # elif not re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{5,18}$', password):  # 密码为5-18位字母和数字的组合
    #     return JsonResponse({'code': 400, 'message': "密码不合法", 'data': {}})
    try:
        new_user = User(phone=phone, password=make_password(password))
        new_user.save()
    except Exception:
        return JsonResponse({'code': 500, 'message': "数据库保存失败", 'data': {}})
    return JsonResponse({'code': 200, 'message': "注册成功", 'data': {}})


def userLogin(request):
    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj.get('phone')
    password = json_obj.get('password')
    if not User.objects.filter(Q(phone=phone)).exists():
        return JsonResponse({'code': 400, 'message': "用户名不存在", 'data': {}})
    else:
        user = User.objects.get(phone=phone)
    if check_password(password, user.password):
        token = make_token(user.uid)
        user.save()
        return JsonResponse({'code': 200, 'message': "登录成功", 'data': {
            'token': token,
            'uid': user.uid,
        }})
    else:
        return JsonResponse({'code': 400, 'message': "密码错误", 'data': {}})


def changePassword(request):
    json_str = request.body
    json_obj = json.loads(json_str)
    oldPassword = json_obj.get('oldPassword')
    newPassword = json_obj.get('newPassword')
    user = request.myUser
    if user.password == oldPassword:
        if re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{5,18}$', newPassword):
            if oldPassword == newPassword:
                return JsonResponse({'code': 400, 'message': '修改后的密码不能与原密码相同', 'data': {}})
            else:
                user.password = newPassword
                try:
                    user.save()
                except Exception as e:
                    print(e)
                    return JsonResponse({'code': 500, 'message': '服务器异常', 'data': {}})
        else:
            return JsonResponse({'code': 400, 'message': '密码不合法', 'data': {}})
    else:
        return JsonResponse({'code': 400, 'message': '原密码错误', 'data': {}})
    if user.password == newPassword:
        return JsonResponse({'code': 200, 'message': '修改密码成功', 'data': {}})



