from rest_framework import routers
from django.urls import path, include
from api import views
from rest_framework import routers
from .routers import UserRouter


router = UserRouter()
router.register(r'users', views.UserViewset, basename='user')
router.register(r'accounts', views.AccountViewset, basename='account')


urlpatterns = [
    path('signin', views.CreateUser.as_view()),
    path('', include(router.urls)),
    path('login', views.Login.as_view()),
    path('logout', views.Logout.as_view()),
]
