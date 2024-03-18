from django.db import models
baseAvatar = "http://rzyi06q9n.hb-bkt.clouddn.com/lufei.jpg"
# Create your models here.
class User(models.Model):
    uid = models.AutoField('uid',primary_key=True)
    username = models.CharField('username', max_length=25)
    password = models.CharField('password', max_length=25)
    name = models.CharField('name', max_length=10)
    phone = models.CharField('phone', default='null', max_length=11)
    email = models.EmailField('email', default='null')
    avatar = models.CharField('avatar',default=baseAvatar,max_length=255)
    is_active = models.BooleanField('is_active', default=True)  # 伪删除字段


class Captcha(models.Model):
    email = models.CharField('email',primary_key = True,max_length=50)
    captcha = models.CharField('captcha',max_length=10)
