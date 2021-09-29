from datetime import date
from django.db import models
from .account import Account
from .User import User


class Bufete(models.Model):
    '''Class to administrate the bufete'''
    name = models.CharField(max_length=60)
    nit = models.CharField(max_length=30)
    web_page = models.URLField(blank=True)
    legal_representative = models.ForeignKey(User,
                                             on_delete=models.CASCADE)
    contact_email = models.EmailField()


class Lawyer(models.Model):
    '''Class to storage the lawyers info'''
    lawyer = models.OneToOneField(User, on_delete=models.CASCADE,
                                primary_key=True)
    professional_card = models.CharField(max_length=20)
    web_page = models.URLField(blank=True)
    linked_in = models.URLField(blank=True)
    active = models.BooleanField(default=False)

    def card_check(self):
        '''call the SIRNA bot to return verify the lawyer status'''
        pass


class UserCalification(models.Model):
    '''Class to storage the users califications'''
    score = models.SmallIntegerField()
    description = models.CharField(max_length=225)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class BufeteCalification(models.Model):
    '''Class to storage the bufete califications'''
    score = models.SmallIntegerField()
    description = models.CharField(max_length=225)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Tag(models.Model):
    '''Class to manage the tags to sort displayed info'''
    branch = models.CharField(max_length=20)
    name = models.CharField(max_length=20)


class Case(models.Model):
    '''This class will be storage the cases information'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    bufete = models.ForeignKey(Bufete, on_delete=models.CASCADE)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)