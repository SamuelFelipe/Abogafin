from rest_framework.routers import Route, DynamicRoute, SimpleRouter
from rest_framework_nested import routers


class UserRouter(SimpleRouter):

    routes = [
            Route(
                url=r'^{prefix}/me{trailing_slash}$',
                mapping={
                         'get': 'self_view',
                         'put': 'update',
                         'delete': 'destroy',
                         'post': 'create',
                         'patch': 'partial_update',
                         },
                name='{basename}-self_view',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}/{lookup}{trailing_slash}$',
                mapping={
                         'get': 'retrieve',
                         },
                name='{basename}-detail',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}{trailing_slash}$',
                mapping={'get': 'list'},
                name='{basename}-list',
                detail=True,
                initkwargs={},
            )
    ]


class CaseRouter(SimpleRouter):

    routes = [
            Route(
                url=r'^{prefix}/me{trailing_slash}$',
                mapping={
                        'get': 'list'
                    },
                name='{basename}-list',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}/{lookup}{trailing_slash}$',
                mapping={
                         'get': 'retrieve',
                         'put': 'update',
                         'delete': 'destroy',
                         'patch': 'partial_update',
                         },
                name='{basename}-detail',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}{trailing_slash}$',
                mapping={
                        'get': 'list'
                    },
                name='{basename}-list',
                detail=True,
                initkwargs={},
            ),
            DynamicRoute(
                url=r'^{prefix}/{lookup}/{url_path}{trailing_slash}$',
                name='{basename}-{url_name}',
                detail=True,
                initkwargs={}
            ),
    ]


class BlogRouter(SimpleRouter):

    routes = [
            Route(
                url=r'^{prefix}/me{trailing_slash}$',
                mapping={
                         'get': 'self_view',
                         'post': 'create',
                         },
                name='{basename}-self_view',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}/{lookup}{trailing_slash}$',
                mapping={
                         'get': 'retrieve',
                         'put': 'update',
                         'patch': 'partial_update',
                         },
                name='{basename}-detail',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}{trailing_slash}$',
                mapping={
                        'get': 'list',
                        },
                name='{basename}-list',
                detail=True,
                initkwargs={},
            )
    ]
