from django.urls import path
from User import views

urlpatterns = [
    path('login', views.userLogin),
    path('register', views.userRegister),
    path('changePwd', views.changePassword),
]
