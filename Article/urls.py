from .views import *
from django.urls import path

urlpatterns = [
    path('', ArticleListOrderedByDate),
    path('read/', ArticleListOrderedByRead),
    path('detail/<int:article_id>/', ArticleDetail),
]