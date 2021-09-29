from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from .account import Account


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


class User(AbstractUser):
    '''
    Personalized user class to match Abogafin user model requeriments
    '''
    # The next 2 lines configures the class
    username = None
    objects = UserManager()


    names = models.CharField(max_length=30)
    surnames = models.CharField(max_length=30)
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
    REQUIRED_FIELDS = ['names', 'surnames', 'cel', 'tel', 'doc_type',
                       'doc_number', 'city']

    def basic_info(self):
        '''Return the basic_info of a user'''
        return {'names': self.names, 'surnames': self.surnames,
                'city': self.city}

    def full_info(self):
        '''Return all the contact info of a user'''
        return {'names': self.names, 'surnames': self.surnames,
                'city': self.city, 'doc_type': self.doc_type,
                'doc_number': self.doc_number, 'mail': self.email,
                'celphone': self.cel, 'phone': self.tel}

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
