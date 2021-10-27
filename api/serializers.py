from rest_framework.reverse import reverse
from blog.models import *
from django.db import IntegrityError, models
from django.core.exceptions import ObjectDoesNotExist
from lawyer_user.models import *
from lawyer_user.User import User
from lawyer_user.account import Account
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
import django.contrib.auth.password_validation as validators


class LawyerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lawyer
        exclude = ['lawyer']
        read_only_fields = ['active', 'last_pc_check']


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
    legal_representative = serializers.HyperlinkedRelatedField(view_name='bufete-detail',
                                                               queryset=Bufete.objects.all(),
                                                               many=True,
                                                               required=False,
                                                               )
    bellow_to = serializers.HyperlinkedRelatedField(view_name='bufete-detail',
                                                    queryset=Bufete.objects.all(),
                                                    many=True,
                                                    required=False,
                                                    )
    lawyer = LawyerSerializer(required=False)

    class Meta:
        model = User
        depth = 1
        fields = ['email' ,'first_name', 'last_name',
                  'doc_type', 'doc_number',
                  'cel', 'tel', 'city', 'account_type',
                  'timesub', 'score', 'publications_user_blog',
                  'lawyer', 'bellow_to',
                  'publications_lawyer_blog',
                  'legal_representative', 'verificated', 'password',
                  ]
        read_only_fields = ['verificated']
        extra_kwargs = {'password': {'write_only': True,},}

    def create(self, validated_data):
        lawyer_data = validated_data.pop('lawyer', None)
        passwd = validated_data.get('password')
        user = User(**validated_data)
        try: # Validate the password, validators in Abogafin/settings.py
            user.set_password(passwd)
            validators.validate_password(password=passwd, user=user,
                                         password_validators=validators.get_default_password_validators())
        except validators.ValidationError as err:
            raise serializers.ValidationError({'password': list(err)})
        try:
            user.save()
        except IntegrityError:
            raise serializers.ValidationError('Account already exist')
        if lawyer_data:
            Lawyer.objects.create(lawyer=user, **lawyer_data)
        return user

    def update(self, instance, validated_data):
        lawyer_data = validated_data.pop('lawyer', None)
        try:
            lawyer =  instance.lawyer
        except ObjectDoesNotExist:
            lawyer = None
        instance =  super().update(instance, validated_data)
        if lawyer and lawyer_data:
            for key, val in lawyer_data.items():
                setattr(lawyer, key, val)
            lawyer.save()
        elif not lawyer and lawyer_data:
            Lawyer.objects.create(lawyer=instance, **lawyer_data)
        return instance


    def validate_account_type(self, value):
        try: # Validate if the account is valid otherwise return an error
            account = Account.objects.get(name=value)
            return account
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Account type does not exist')

# The email must be aviable to update, for that reason this check must be done
# in the create method, if we check it in a validate_* if the user doesn't
# change email the function always will raise an error.
#
#   def validate_email(self, value):
#       try:
#           User.objects.get(email=value)
#           raise serializers.ValidationError('Account already exist')
#       except ObjectDoesNotExist:
#           return value


class PublicUserSerializer(serializers.ModelSerializer):

    account_type = serializers.SlugRelatedField(slug_field='name',
                                                read_only=True,
                                                )
    legal_representative = serializers.HyperlinkedRelatedField(view_name='bufete-detail',
                                                               read_only=True,
                                                               many=True,
                                                               )
    bellow_to = serializers.HyperlinkedRelatedField(view_name='bufete-detail',
                                                    read_only=True,
                                                    many=True,
                                                    )
    lawyer = LawyerSerializer()

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


class UserCalificationSerializer(serializers.ModelSerializer):

    owner = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                lookup_field='email',
                                                read_only=True)
    target = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                 lookup_field='email',
                                                 read_only=True)

    class Meta:
        model = UserCalification
        fields = '__all__'

    def create(self, validated_data):
        return UserCalification(**validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate_score(self, value):
        if value > 5.0 or value < 0.0:
            raise serializers.ValidationError('score is a float between 0 and 5')
        return value

    def validate_description(self, value):
        if len(value) < 15:
            raise serializers.ValidationError('Description must have aleast 15 characters')
        return value


class BufeteSerializer(serializers.ModelSerializer):

    legal_representative = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                               lookup_field='email',
                                                               read_only=True)
    lawyers = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                  many=True,
                                                  lookup_field='email',
                                                  queryset=User.objects.all(),
                                                  required=False, default=[])

    class Meta:
        model = Bufete
        fields = ['id', 'name', 'nit', 'web_page', 'legal_representative',
                  'contact_email', 'lawyers', 'score',]


class BufeteCalificationSerializer(serializers.ModelSerializer):

    owner = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                lookup_field='email',
                                                read_only=True)
    target = serializers.HyperlinkedRelatedField(view_name='bufete-detail',
                                                 lookup_field='pk',
                                                 read_only=True)

    class Meta:
        model = BufeteCalification
        fields = '__all__'


class InterestedSerializer(serializers.ModelSerializer):

    user = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                               lookup_field='email',
                                               read_only=True)
    bufete = serializers.HyperlinkedRelatedField(view_name='bufete-detail',
                                                 read_only=True)

    class Meta:
        model = Interested
        fields = ['user', 'bufete',]


class PublicCaseSerializer(serializers.ModelSerializer):

    owner = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                lookup_field='email',
                                                read_only=True)
    interested = InterestedSerializer(many=True)

    class Meta:
        model = Case
        fields = ['id', 'title', 'description',
                  'created_at', 'updated_at', 'tag']


class CaseSerializer(serializers.ModelSerializer):

    owner = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                lookup_field='email',
                                                read_only=True)
    in_representation_of = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                               lookup_field='email',
                                                               read_only=True)
    bufete = serializers.HyperlinkedRelatedField(view_name='bufete-detail',
                                                 read_only=True)
    interested = InterestedSerializer(many=True)

    class Meta:
        model = Case
        fields = '__all__'


class BlogpostSerializer(serializers.ModelSerializer):

    owner = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                lookup_field='email',
                                                read_only=True)
    type = serializers.ChoiceField([
             ('NT', 'Noticias'),
             ('LB', 'Blog de abogados'),
             ('UB', 'Blog de Usuarios')
            ], default='UB')

    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'tags', 'score', 'owner',
                  'created_at', 'updated_at', 'type',
                  ]
        extra_kwargs = {'tags': {'required': False}}


class BlogCalificationSerializer(serializers.ModelSerializer):

    owner = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                lookup_field='email',
                                                read_only=True)
    blog = serializers.HyperlinkedRelatedField(view_name='blog-detail',
                                               read_only=True)

    class Meta:
        model = BlogCalification
        fields = '__all__'


class BlogCommentSerializer(NestedHyperlinkedModelSerializer):

    parent_lookup_kwargs = {
                'blog_pk': 'blog__pk',
            }

    owner = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                lookup_field='email',
                                                read_only=True)
    blog = serializers.HyperlinkedRelatedField(view_name='blog-detail',
                                               read_only=True)

    class Meta:
        model = BlogComment
        fields = '__all__'


class BlogCommentNestedUrl(serializers.HyperlinkedRelatedField):

    view_name = 'blogcomment-detail'

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
                'pk': obj.pk,
                'blog_pk': self.parent.context['request'].path[7],
                }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class ResponceSerializer(NestedHyperlinkedModelSerializer):

    parent_lookup_kwargs = {
                'blogcomment_pk': 'blog_comment__pk',
                'blog_pk': 'blog_comment__blog__pk',
            }
    owner = serializers.HyperlinkedRelatedField(view_name='user-detail',
                                                lookup_field='email',
                                                read_only=True)
    blog_comment = BlogCommentNestedUrl(read_only=True)

    class Meta:
        model = Responce
        fields = '__all__'
