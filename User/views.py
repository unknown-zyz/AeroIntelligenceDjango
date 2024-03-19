import datetime
import json
import re

from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse

from Tools.EmailCheck import emailCheck, createCaptcha
# from Tools.LoginCheck import loginCheck
from Tools.MakeToken import make_token
from Tools.QiNiuYun import uploadFile
from User.models import *
from django.contrib.auth.hashers import make_password,check_password


# 注册
def userRegister(request):
    json_str = request.body
    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    password = json_obj.get('password')
    confirmPassword = json_obj.get('confirmPassword')
    phone = json_obj.get('phone')
    email = json_obj.get('email')
    name = json_obj.get('name')
    captcha = json_obj.get('captcha')
    avatar = json_obj.get('avatar')
    usernameToString = str(username)
    if password != confirmPassword:
        return JsonResponse({'code': 400, 'message': "两次密码不同", 'data': {}})
    elif not usernameToString.isalnum():
        return JsonResponse({'code': 400, 'message': "用户名不合法", 'data': {}})
    elif User.objects.filter(Q(username=username) & Q(is_active=True)).exists():
        return JsonResponse({'code': 400, 'message': "用户名已存在", 'data': {}})
    elif not re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{5,18}$', password):  # 密码为5-18位字母和数字的组合
        return JsonResponse({'code': 400, 'message': "密码不合法", 'data': {}})
    elif not re.match('^1\d{10}$', phone):
        return JsonResponse({'code': 400, 'message': "手机号不合法", 'data': {}})
    elif User.objects.filter(phone=phone).exists():
        return JsonResponse({'code': 400, 'message': "手机号已存在", 'data': {}})
    elif not re.match('^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', email):
        return JsonResponse({'code': 400, 'message': "邮箱不合法", 'data': {}})
    elif User.objects.filter(email=email).exists():
        return JsonResponse({'code': 400, 'message': "邮箱已被使用", 'data': {}})
    else:
        correctCaptcha = Captcha.objects.get(email=email)
        if correctCaptcha.captcha != captcha:
            return JsonResponse({'code': 400, 'message': "验证码错误", 'data': {}})
        else:
            newUser = User(username=username, password=make_password(password), phone=phone, email=email, name=name)
            if avatar: newUser.avatar = avatar
            try:
                newUser.save()
            except Exception as e:
                return JsonResponse({'code': 500, 'message': "服务器异常", 'data': {}})
    try:
        newUser.save()
    except Exception as e:
        return JsonResponse({'code': 500, 'message': "数据库保存失败", 'data': {}})
    return JsonResponse({'code': 200, 'message': "注册成功", 'data': {}})


def userLogin(request):
    json_str = request.body
    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    password = json_obj.get('password')
    if not User.objects.filter(Q(username=username) & Q(is_active=True)).exists():  # 用户名是否存在
        return JsonResponse({'code': 400, 'message': "用户名不存在", 'data': {}})
    else:
        user = User.objects.get(username=username)
    if check_password(password, user.password):
        token = make_token(user.uid)
        # user.logincnt +=1
        user.save()
        return JsonResponse({'code': 200, 'message': "登录成功", 'data': {
            'token': token,
            'uid': user.uid,
            # 'logincnt': user.logincnt,
        }})
    else:
        return JsonResponse({'code': 400, 'message': "密码错误", 'data': {}})


def sendCaptcha(request):
    json_str = request.body
    json_obj = json.loads(json_str)
    email = json_obj.get('email')
    captcha = createCaptcha()
    if Captcha.objects.filter(email=email).exists():
        oldCaptcha = Captcha.objects.get(email=email)
        oldCaptcha.captcha = captcha
        oldCaptcha.save()
    else:
        newCaptcha = Captcha(email=email, captcha=captcha)
        newCaptcha.save()
    emailCheck(email, captcha)
    return JsonResponse({'code': 200, 'message': "验证码发送成功", 'data': {}})


# @loginCheck
def changeInformation(request):  # 修改个人信息
    user = request.myUser
    json_str = request.body
    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    phone = json_obj.get('phone')
    email = json_obj.get('email')
    if not username.isalnum():
        return JsonResponse({'code': 400, 'message': "用户名不合法", "data": {}})
    if User.objects.filter(Q(username=username) & Q(is_active=True)).exists() and username != user.username:
        return JsonResponse({'code': 400, 'message': "用户名已存在", "data": {}})
    if not re.match('^1\d{10}$', phone):
        return JsonResponse({'code': 400, 'message': "手机号不合法", "data": {}})
    if User.objects.filter(Q(phone=phone) & Q(is_active=True)).exists() and phone != user.phone:
        return JsonResponse({'code': 400, 'message': "手机号已被使用", "data": {}})
    if not re.match('^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', email):
        return JsonResponse({'code': 400, 'message': "邮箱不合法", "data": {}})
    if User.objects.filter(Q(email=email) & Q(is_active=True)).exists() and email != user.email:
        return JsonResponse({'code': 400, 'message': "邮箱已被使用", "data": {}})
    if username == user.username and phone == user.phone and email == user.email:
        return JsonResponse({'code': 400, 'message': "没有要修改的信息", "data": {}})
    user.username = username
    user.phone = phone
    user.email = email
    try:
        user.save()
        return JsonResponse({'code': 200, 'message': "修改信息成功", "data": {}})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': "服务器异常", "data": {}})


# @loginCheck
def changePassword(request):  # 修改密码
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


# @loginCheck
def changeAvatar(request):  # 修改头像
    key = request.POST.get("key")
    file = request.FILES.get("file")
    user = request.myUser
    nowTime = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")  # 当前时间
    filename = "".join(nowTime.split()) + "_" + key
    code = uploadFile(filename, file)
    if code == 400:
        return JsonResponse({'code': 400, 'message': "上传失败", "data": {}})
    else:
        user.avatar = code
        user.save()
        return JsonResponse({'code': 200, 'message': "上传成功", "data": {"url": code}})


def pwdFind(request):  # 找回密码验证
    json_str = request.body
    json_obj = json.loads(json_str)
    email = json_obj.get("email")
    captcha = json_obj.get("captcha")
    pwd = json_obj.get("newPassword")
    user1 = User.objects.get(email=email)
    user2 = Captcha.objects.get(email=email)
    if user2.captcha != captcha:
        return JsonResponse({'code': 400, 'message': '验证码错误', 'data': {}})
    if not re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{5,18}$', pwd):
        return JsonResponse({'code': 400, 'message': '密码不合法', 'data': {}})
    try:
        user1.password = pwd
        user1.save()
        return JsonResponse({'code': 200, 'message': '修改密码成功', 'data': {}})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': '服务器异常', 'data': {}})


# @loginCheck
def showInfo(request):  # 返回个人信息
    user = request.myUser
    data = model_to_dict(user)
    result = {"code": 200, "message": "成功返回用户信息", 'data': {'info': data}}
    return JsonResponse(result)
