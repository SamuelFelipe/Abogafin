from rest_framework_nested import routers
from django.urls import path, include
from api import views
from .routers import UserRouter, CaseRouter, BlogRouter


blogrouter = BlogRouter()
blogrouter.register(r'blogs', views.BlogpostViewset, basename='blog')

## Base router
#
# 'me' is a wild card to show related info of the user how call the api.
# changes to related items only can be done through '{prefix}/me/**' endpoints
#
## generates:
#       /{prefix}/ :: {basename}-list :: show all entries
#       /{prefix}/me/ :: {basename}-self_view :: show all own info
#       /{prefix}/{lookup}/ :: {basename}-detail :: public entity info
router = UserRouter()
router.register(r'users', views.UserViewset, basename='user')
router.register(r'bufetes', views.BufeteViewset, basename='bufete')
router.register(r'accounts', views.AccountViewset, basename='account')

case_router = CaseRouter()
case_router.register(r'cases', views.CaseViewset, basename='case')

## generates:
#       /users/{me|user_email}/{califications|comentaries}/
#       /users/{me|user_email}/{califications|comentaries}/{pk}/
ucommentaries_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
ucommentaries_router.register(r'califications', views.UserCalificationsViewset)
ucommentaries_router.register(r'commentaries', views.UserCommentariesViewset)

## generates:
#       /bufetes/{me|bufete_id}/califications/
#       /bufetes/{me|bufete_id}/califications/{pk}/
bcommentaries_router = routers.NestedSimpleRouter(router, r'bufetes', lookup='bufete')
bcommentaries_router.register(r'califications', views.BufeteCalificationsViewset)

blognested_router = routers.NestedSimpleRouter(blogrouter, r'blogs', lookup='blog')
blognested_router.register(r'califications', views.BlogCalificationViewset)
blognested_router.register(r'commentaries', views.BlogCommentViewset)

response_router = routers.NestedSimpleRouter(blognested_router, r'commentaries', lookup='blogcomment')
response_router.register(r'responses', views.ResponceViewset, basename='responce')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(blogrouter.urls)),
    path('', include(blognested_router.urls)),
    path('', include(response_router.urls)),
    path('', include(case_router.urls)),
    path('', include(ucommentaries_router.urls)),
    path('', include(bcommentaries_router.urls)),
    path('signup/', views.CreateUser.as_view()),
    path('login/', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),
]
