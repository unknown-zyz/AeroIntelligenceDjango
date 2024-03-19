from django.urls import path
from .views import *

urlpatterns = [
    path('', BrowseRecordList.as_view()),
    path('<int:pk>/', BrowseRecordDestroy.as_view()),
]
