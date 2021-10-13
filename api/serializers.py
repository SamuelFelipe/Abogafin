from django.core.exceptions import ObjectDoesNotExist
from lawyer_user.models import *
from lawyer_user.User import User
from lawyer_user.account import Account
from rest_framework import serializers
import django.contrib.auth.password_validation as validators


class UserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    cel = serializers.CharField(max_length=12)
    tel = serializers.CharField(max_length=12)
    doc_type = serializers.ChoiceField([('CC', 'Cédula de Ciudadanía'),
                                        ('CE', 'Cédula de Extranjería')])
    doc_number = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=30)
    account_type = serializers.SlugRelatedField(slug_field='name',
                                                queryset=Account.objects.all(),
                                                default='Default',
                                                )
    verificated = serializers.BooleanField(read_only=True)
    legal_representative = serializers.SlugRelatedField(slug_field='name',
                                                        many=True,
                                                        queryset=Bufete.objects.all(),
                                                        required=False,
                                                        )
    bellow_to = serializers.SlugRelatedField(slug_field='name',
                                             many=True,
                                             queryset=Bufete.objects.all(),
                                             required=False,
                                             )

    class Meta:
        model = User
        fields = ['email' ,'first_name', 'last_name',
                  'doc_type', 'doc_number',
                  'cel', 'tel', 'city', 'account_type',
                  'timesub', 'score', 'publications_user_blog',
                  'lawyer', 'bellow_to',
                  'publications_lawyer_blog',
                  'legal_representative', 'verificated',
                  ]
        read_only_fields = ['verificated']
        extra_kwargs = {'password': {'write_only': 'True'},}


    def create(self, validated_data):
        passwd = validated_data.get('password')
        user = User(**validated_data)
        try: # Validate the password, validators in Abogafin/settings.py
            user.set_password(passwd)
            validators.validate_password(password=passwd, user=user,
                                         password_validators=validators.get_default_password_validators())
        except validators.ValidationError as err:
            raise serializers.ValidationError({'password': list(err)})
        user.save()
        return user

    def validate_account_type(self, value):
        try: # Validate if the account is valid otherwise return an error
            account = Account.objects.get(name=value)
            return account
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Account type does not exist')

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            raise serializers.ValidationError('Account already exist')
        except ObjectDoesNotExist:
            return value


class PublicUserSerializer(serializers.ModelField):

    account_type = serializers.SlugRelatedField(slug_field='name',
                                                read_only=True,
                                                )

    class Meta:
        model = User
        fields = ['email' ,'first_name', 'last_name',
                  'city', 'account_type',
                  'timesub', 'score', 'publications_user_blog',
                  'lawyer', 'bellow_to',
                  'publications_lawyer_blog',
                  'legal_representative',
                  ]
        read_only_fields = ['verificated']


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['name', 'max_postulations', 'max_active_cases',
                  'price', 'users',
                  ]
        extra_kwargs = {'url': {'lookup_field': 'name'}}
