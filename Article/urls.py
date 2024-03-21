from .views import *
from django.urls import path

urlpatterns = [
    path('search/', search),
    path('doc/<int:article_id>/', getDoc),
]