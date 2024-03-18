from django.urls import path
from Tag.views import *

urlpatterns = [
    path('', TagList.as_view()),
]
