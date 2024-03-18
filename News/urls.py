from django.urls import path
from News.views import *

urlpatterns = [
    path('', NewsListOrderedByDate.as_view()),
    path('click/', NewsListOrderedByClick.as_view()),
    path('<int:pk>/', NewsDetail.as_view()),
]
