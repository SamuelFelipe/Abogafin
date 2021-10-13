from rest_framework.routers import Route, DynamicRoute, SimpleRouter


class UserRouter(SimpleRouter):
    """
    A router for read-only APIs, which doesn't use trailing slashes.
    """
    routes = [
            Route(
                url=r'^{prefix}/me$',
                mapping={
                         'get': 'self_view',
                         'post': 'publicate',
                         'put': 'update',
                         'delete': 'delete',
                         },
                name='{basename}-self_view',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}/{lookup}$',
                mapping={'get': 'retrieve'},
                name='{basename}-detail',
                detail=True,
                initkwargs={},
            ),
            Route(
                url=r'^{prefix}$',
                mapping={'get': 'list'},
                name='{basename}-list',
                detail=True,
                initkwargs={}
            )
    ]
