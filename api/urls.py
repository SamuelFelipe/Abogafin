from rest_framework_nested import routers
from django.urls import path, include
from api import views
from .routers import UserRouter


router = UserRouter()
router.register(r'users', views.UserViewset, basename='user')
router.register(r'bufetes', views.BufeteViewset, basename='bufete')
router.register(r'accounts', views.AccountViewset, basename='account')

comentaries_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
comentaries_router.register(r'califications', views.UserCalificationViewset)
comentaries_router.register(r'comentaries', views.UserComentariesViewset)

urlpatterns = [
    path('signin', views.CreateUser.as_view()),
    path('', include(router.urls)),
    path('', include(comentaries_router.urls)),
    path('login', views.Login.as_view()),
    path('logout', views.Logout.as_view()),
]
