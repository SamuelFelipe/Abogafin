from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from lawyer_user.models import *
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .permissions import Cookies, OwnerOrOnlyRead
from .serializers import *


class Login(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request.session['id'] = request.user.id
        request.session['email'] = request.user.email
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        request.session['id'] = request.user.id
        request.session['email'] = request.user.email
        return Response(status=status.HTTP_200_OK)


class Logout(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        request.session.flush()
        return Response(status=status.HTTP_200_OK)


class CreateUser(GenericAPIView, mixins.CreateModelMixin):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(self.serializer_class(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewset(viewsets.ModelViewSet):
    permission_classes = [Cookies]
    queryset = User.objects.all()
    lookup_field = 'email'
    lookup_value_regex = '[\w@.]+'


    def get_serializer_class(self):
        try:
            if self.request.path[1:].split('/')[1] == 'me':
                return UserSerializer
            return PublicUserSerializer
        except IndexError:
            return PublicUserSerializer

    def self_view(self, request):
        id = request.session['id']
        user = User.objects.get(pk=id)
        context = {'request': request}
        serializer = self.get_serializer_class()
        return Response(serializer(user, context=context).data)

    def update(self, request):
        id = request.session['id']
        user = User.objects.get(pk=id)
        context = {'request': request}
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(user, data=request.data, context=context)
        if serializer.is_valid():
            return Response(serializer_class(serializer.save(), context=context).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def list(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, email=None):
        context = {'request': request}
        user = self.get_object()
        serializer = self.get_serializer_class()
        return Response(serializer(user, context=context).data)


class AccountViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    lookup_field = 'name'

    def self_view(self, request):
        try:
            id = request.session['id']
            user = User.objects.get(pk=id)
            context = {'request': request}
            return Response(self.serializer_class(user.account_type,
                                                  context=context).data)
        except KeyError:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_403_FORBIDDEN)


class UserCalificationViewset(viewsets.ModelViewSet):
    permission_classes = [OwnerOrOnlyRead]
    serializer_class = UserCalificationSerializer
    queryset = UserCalification.objects.all()
    pagination_class = PageNumberPagination


    def self_view(self, request):
        try:
            id = request.session['id']
            user = User.objects.get(pk=id)
            context = {'request': request}
            return Response(self.serializer_class(user.comentaries.get(),
                                                  context=context).data)
        except KeyError:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_403_FORBIDDEN)

    def list(self, request, user_email=None, id=None):
        context = {'request': request}
        if user_email == 'me':
            user_id = request.session['id']
        else:
            user_id = User.objects.get(email=user_email).pk
        user = User.objects.get(pk=user_id)
        queryset = UserCalification.objects.filter(target=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def create(self, request, user_email=None):
        context = {'request': request}
        serializer = self.serializer_class(data=request.data)
        target = User.objects.get(email=user_email)
        owner = User.objects.get(pk=request.session['id'])
        if owner == target:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            com = serializer.save(owner=owner, target=target)
            return Response(self.serializer_class(com.save(),
                                                  context=context).data)
        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UserComentariesViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [OwnerOrOnlyRead]
    serializer_class = UserCalificationSerializer
    queryset = UserCalification.objects.all()


    def list(self, request, user_email=None, id=None):
        context = {'request': request}
        if user_email == 'me':
            user_id = request.session['id']
        else:
            user_id = User.objects.get(email=user_email).pk
        user = User.objects.get(pk=user_id)
        queryset = UserCalification.objects.filter(owner=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BufeteViewset(viewsets.ModelViewSet):
    permission_classes = [Cookies]
    serializer_class = BufeteSerializer
    queryset = Bufete.objects.all()
