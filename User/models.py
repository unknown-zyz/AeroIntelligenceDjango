from django.db import models

class User(models.Model):
    uid = models.AutoField('uid',primary_key=True)
    phone = models.CharField('phone', default='null', max_length=11)
    password = models.CharField('password', max_length=25)


