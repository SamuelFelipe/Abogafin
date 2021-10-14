from rest_framework.routers import Route, DynamicRoute, SimpleRouter
from rest_framework_nested import routers


class UserRouter(SimpleRouter):

    routes = [
            Route(
                url=r'^{prefix}/me$',
                mapping={
                         'get': 'self_view',
                         'put': 'update',
                         'delete': 'delete',
                         },
                name='{basename}-self_view',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}/{lookup}$',
                mapping={
                         'get': 'retrieve',
                         },
                name='{basename}-detail',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}$',
                mapping={'get': 'list'},
                name='{basename}-list',
                detail=True,
                initkwargs={},
            )
    ]
