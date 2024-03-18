from django.urls import path
from Books.views import *

urlpatterns = [
    path('', BookListCreate.as_view()),
    path('<int:pk>/', BookRetrieveUpdateDestroy.as_view()),
]
