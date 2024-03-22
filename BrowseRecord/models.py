from django.db import models

from User.models import User


class BrowseRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article_id = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

