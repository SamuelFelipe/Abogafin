from lawyer_user import views as views_main
from blog import views as views_blog
from django.urls import path


urlpatterns = [
    path('', views_main.home, name='home'),
    path('noticias/', views_main.blog, name='noticias')
]
