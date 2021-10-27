from datetime import date
from django.db import models
from .account import Account
from .User import User


class Bufete(models.Model):
    '''
Class to administrate the bufete

Attributes:
    pk/id: Primary key, it's an autoincremental integer
    name: bufete name
    nit: 'Número de Identificación Tributaria' Colombians company identificator
    legal_representative: User who represent the company
    contact_email: Company contact email
    lawyers: Many to many relation ship with all the users in the bufete
'''
    name = models.CharField(max_length=60)
    nit = models.CharField(max_length=30, unique=True)
    web_page = models.URLField(blank=True, null=True)
    legal_representative = models.ForeignKey(User,
                                             on_delete=models.CASCADE,
                                             related_name='legal_representative')
    contact_email = models.EmailField()
    lawyers = models.ManyToManyField(User, related_name='bellow_to')

    def score(self):
        cals = BufeteCalification.objects.all().filter(target=self.pk)
        avg = [cal.score for cal in cals]
        if len(avg):
            return sum(avg) / len(avg)
        return None


class Lawyer(models.Model):
    '''
Class to storage the lawyers info

Attributes:
    pk/id: Primary key, it's an autoincremental integer
    lawyer: One to one relationship with user class
    professional_card: Lawyer professional card
    web_page: Lawyer webpage
    linked_in: --
    facebook: --
    active: By default false, after SIRNA bot checks the lawyer card
            it could change.
    last_pc_check = date of the last check doned by the SIRNA bot
'''
    lawyer = models.OneToOneField(User, on_delete=models.CASCADE,
                                  primary_key=True)
    professional_card = models.CharField(max_length=20)
    web_page = models.URLField(blank=True)
    linked_in = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    active = models.BooleanField(default=False)
    last_pc_check = models.DateField(default=None, blank=True, null=True)

    def card_check(self):
        '''call the SIRNA bot to return verify the lawyer status'''
        pass


class UserCalification(models.Model):
    '''
Class to storage the users califications


Attributes:
    pk/id: Primary key, it's an autoincremental integer
    owner: user who write it
    score: 1 to 5 calification
    description: --
    target_user: --
'''
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='owner')
    score = models.SmallIntegerField()
    description = models.CharField(max_length=225)
    target = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='comentaries')


class BufeteCalification(models.Model):
    '''Class to storage the bufete califications'''
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.SmallIntegerField()
    description = models.CharField(max_length=225)
    target = models.ForeignKey(Bufete, on_delete=models.CASCADE)


class Tag(models.Model):
    '''Class to manage the tags to sort displayed info'''
    branch = models.CharField(max_length=20)
    name = models.CharField(max_length=20)


class Case(models.Model):
    '''This class will be storage the cases information'''
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=2500)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    election_date = models.DateTimeField(blank=True)
    in_representation_of = models.ForeignKey(User,
                                             on_delete=models.SET_NULL,
                                             null=True,
                                             related_name='represented_by')
    bufete = models.ForeignKey(Bufete, on_delete=models.SET_NULL,
                               null=True)
    tag = models.ManyToManyField(Tag)


class Interested(models.Model):
    '''Represent the relation bettwen the layers/bufetes and the cases'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bufete = models.ForeignKey(Bufete, on_delete=models.CASCADE, null=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE,
                             related_name='interested')
