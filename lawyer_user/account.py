from django.db import models


class Account(models.Model):
    '''
Class to manage accounts types
    
Attributes:
    pk/id: Primary key, it's an autoincremental integer
    name*: Account Name; unique
    max_postulations*: limit of postulations to the users cases
    max_active_cases*: limit of active casses
    price*: per month subscrition cost
    '''
    name = models.CharField(max_length=20, unique=True)
    max_postulations = models.SmallIntegerField()
    max_active_cases = models.SmallIntegerField()
    price = models.FloatField()

    def __str__(self):
        return self.name

    def info(self):
        return {'id': self.pk, 'name': self.name,
                'max_postulations': self.max_postulations,
                'max_active_cases': self.max_active_cases,
                'price': self.price
                }

    def users(self):
        from .User import User
        return User.objects.filter(account_type=self).count()
