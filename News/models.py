from django.db import models
from Tag.models import Tag


class News(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.CharField(max_length=50)
    click_count = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.title
