from django.urls import path
from .views import *

urlpatterns = [
    path('', BrowseRecordListCreate.as_view()),
    path('<int:pk>/', BrowseRecordDestroy.as_view()),
]
