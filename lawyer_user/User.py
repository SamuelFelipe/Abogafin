from datetime import date
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from .account import Account
from .models import *


class UserManager(BaseUserManager):
    '''
    This class allow to manage te new user with out username
    methods are almost the same that BaseUserManager, here we remove the
    username.
    '''
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    '''
    Personalized user class to match Abogafin user model requeriments
    '''
    # The next 2 lines configures the class
    objects = UserManager()

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    cel = models.CharField(max_length=12)
    tel = models.CharField(max_length=12)
    documents = [
            ('CC', 'Cédula de Ciudadanía'),
            ('CE', 'Cédula de Extranjería')
            ]
    doc_type = models.CharField(max_length=2, choices=documents)
    doc_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    city = models.CharField(max_length=30)
    account_type = models.ForeignKey(Account, on_delete=models.SET_NULL,
            null=True)
    verificated = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'cel', 'tel', 'doc_type',
            'doc_number', 'city']


    def basic_info(self):
        '''
Return the basic_info of a user
Used to retrieve the public info in the api.
        '''
        basic_user_info = {'names': self.first_name, 'surnames': self.last_name,
                'city': self.city, 'has_bufete': self.has_bufete(),
                'is_lawyer': self.is_lawyer(),
                'in_bufete': self.bellow_bufete(),
                'users_blog_posts': self.UBlogCount(),
                'lawyer_blog_posts': self.ABlogCount(),
                'days_here': self.timesub(),
                'calification': self.score(),
                }
        if basic_user_info['is_lawyer']:
            basic_user_info['is_active_lawyer'] = self.lawyer.active
        if basic_user_info['has_bufete']:
            basic_user_info['legal_representative_of'] = [obj.info() for obj in self.legal_representative.all()]
        if basic_user_info['in_bufete']:
            basic_user_info['bellow_to'] = [obj.info() for obj in self.bellow_to.all()]
        return basic_user_info

    def full_info(self):
        '''Return all the contact info of a user'''
        full_user_info = {'names': self.first_name, 'surnames': self.last_name,
                'city': self.city, 'doc_type': self.doc_type,
                'doc_number': self.doc_number, 'mail': self.email,
                'celphone': self.cel, 'phone': self.tel,
                'is_lawyer': self.is_lawyer(),
                'has_bufete': self.has_bufete(),
                'users_blog_posts': self.UBlogCount(),
                'lawyer_blog_posts': self.ABlogCount(),
                'account_type': self.account_type.name,
                'calification': self.score(),
                'days_here': self.timesub(),
                }
        if self.is_lawyer():
            full_user_info['lawyer_information'] = self.lawyer.info()
        if self.has_bufete():
            full_user_info['legal_representative_of'] = [obj.info() for obj in self.legal_representative.all()]
        return full_user_info

    def is_lawyer(self):
        '''
        Return True if the user is register like lawyer
        this method doesn't verify if the lawyer has a valid or
        active professional card.
        '''
        try:
            if self.lawyer:
                return True
        except:
            return False

    def has_bufete(self):
        '''
        Return True if the user is register in a bufete
        '''
        if len(self.legal_representative.all()):
            return True
        return False

    def bellow_bufete(self):
        if len(self.bellow_to.all()):
            return True
        return False

    def UBlogCount(self):
        from blog.models import BlogPost
        return BlogPost.objects.filter(owner=self.pk, type='UB').count()

    def ABlogCount(self):
        from blog.models import BlogPost
        return BlogPost.objects.filter(owner=self.pk, type='AB').count()

    def timesub(self):
        return (date.today() - self.created_at).days

    def score(self):
        from .models import UserCalification
        cals = UserCalification.objects.all().filter(target_user=self.pk)
        avg = [cal.score for cal in cals]
        if len(avg):
            return sum(avg) / len(avg)
        return None
