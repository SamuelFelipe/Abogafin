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
Personalized user class to match Abogafin MVP users requeriments

Attributes:
    pk/id: Primary key, it's an autoincremental integer
    created_at: Object cretate date
    updated_at: Object last update date
    first_name*: --
    last_name*: --
    cel*: cell phone number
    tel: telephone number
    doc_type*: Document type, choice options in <documents>
    doc_number*: Document number
    email*: --
    city*: --
    account_type: Account which user is subscribed
    verificated: By default false, it change if the user verify his email,
                 When email is not verificated User can't interact in the
                 platform.
    '''
    # The next 2 lines configures the class
    objects = UserManager()

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    cel = models.CharField(max_length=12)
    tel = models.CharField(max_length=12, blank=True)
    documents = [
            ('CC', 'Cédula de Ciudadanía'),
            ('CE', 'Cédula de Extranjería')
            ]
    doc_type = models.CharField(max_length=2, choices=documents)
    doc_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True, max_length=50)
    city = models.CharField(max_length=30)
    account_type = models.ForeignKey(Account, on_delete=models.SET_NULL,
            null=True)
    verificated = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'cel', 'tel', 'doc_type',
            'doc_number', 'city']

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

    def publications_user_blog(self):
        '''
Return the amount of blogs user has publicate user blog
        '''
        from blog.models import BlogPost
        return BlogPost.objects.filter(owner=self.pk, type='UB').count()

    def publications_lawyer_blog(self):
        '''
Return the amount of blogs user has publicate in lawyer blog
        '''
        from blog.models import BlogPost
        return BlogPost.objects.filter(owner=self.pk, type='AB').count()

    def timesub(self):
        '''
Return the age of the account in days
        '''
        return (date.today() - self.created_at).days

    def score(self):
        '''
Return the user score.
Score is calculated only by the user commentaries,
user blogs have they own score
        '''
        from .models import UserCalification
        cals = UserCalification.objects.all().filter(target=self.pk)
        avg = [cal.score for cal in cals]
        if len(avg):
            return sum(avg) / len(avg)
        return None
