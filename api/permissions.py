from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.models import Session


class Cookies(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        try:
            Session.objects.get(session_key=request.session._session_key)
            return True
        except ObjectDoesNotExist:
            return False


class OwnerOrOnlyRead(Cookies):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner.id == request.session['id']
