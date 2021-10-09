from rest_framework import routers
from django.urls import path
from api import views


urlpatterns = [
    path('stats', views.Stats.as_view()),
    path('users/me', views.Selfview.as_view()),
    path('users/<int:pk>', views.Userview.as_view()),
    path('accounts', views.Accountsview.as_view()),
    path('accounts/<int:pk>', views.Accountview.as_view()),
    path('create_user', views.CreateUser.as_view()),
]
