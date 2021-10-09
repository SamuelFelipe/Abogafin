from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework.views import APIView
from lawyer_user.User import User
from lawyer_user.account import Account
from lawyer_user.models import *
from rest_framework.response import Response
from rest_framework import permissions, status
import django.contrib.auth.password_validation as validators
from django.core.validators import validate_email
from .permissions import *



class Selfview(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = User.objects.get(pk=request.user.pk)
        return Response(user.full_info())


class Userview(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        user = User.objects.get(pk=pk)
        return Response(user.basic_info())


class Stats(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        bufetes = Bufete.objects.count()
        users = User.objects.count()
        return Response({
                         'users': users,
                         'bufete': bufetes,
                         'total': bufetes + users
                        })


class Accountsview(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        accounts = Account.objects.all().values()
        return Response(accounts)


class Accountview(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, format=None):
        return Response(Account.objects.get(pk=pk).info())


class CreateUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        '''
Create a new user
'''
        info = request.data
        if not info:
            return Response({'details': 'empty data'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not info.get('email'):
            return Response({'detail': 'Email field is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        account_name = info.get('account_type', 'Default')
        try: # account must be valid
            account = Account.objects.get(name=account_name)
        except ObjectDoesNotExist:
            return Response({'details': 'The account type does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)
        info['account_type'] = account
        info.pop('pk', None)
        info.pop('id', None)
        passwd = info.get('password')
        if not passwd:
            return Response({'details': 'Password is needed'},
                            status=status.HTTP_400_BAD_REQUEST)
        new_user = User(**info)
        try: # Validate the password and email
            new_user.set_password(passwd)
            validators.validate_password(password=passwd,
                                         user=new_user, 
                                         password_validators=validators.get_default_password_validators()
                                        )
            validate_email(new_user.email)
        except validators.ValidationError as err:
            return Response({'details': err})
        try: # If this fails it means the email is already on use
            new_user.save()
        except IntegrityError:
            return Response({'details': 'The email is already in use'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(new_user.full_info(), status=status.HTTP_201_CREATED)
