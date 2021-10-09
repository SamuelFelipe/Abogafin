from django.db import models


class Account(models.Model):
    '''Class to manage accounts types'''
    name = models.CharField(max_length=20)
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
