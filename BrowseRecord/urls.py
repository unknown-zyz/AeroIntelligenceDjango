from django.urls import path
from .views import *

urlpatterns = [
    path('', BrowseRecordList.as_view()),
    path('delete/', BrowseRecordDestroy.as_view()),
]
