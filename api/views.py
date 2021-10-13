from rest_framework.decorators import action
from lawyer_user.models import *
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .permissions import Cookies
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

    def list(self, request):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, email):
        context = {'request': request}
        user = self.get_object()
        serializer = self.get_serializer_class()
        return Response(serializer(user, context=context).data)


class AccountViewset(viewsets.ModelViewSet):
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
