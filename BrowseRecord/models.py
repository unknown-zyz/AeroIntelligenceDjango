from django.db import models

from News.models import News
from User.models import User


class BrowseRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

