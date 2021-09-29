from django.db import models


class Account(models.Model):
    '''Class to manage accounts types'''
    name = models.CharField(max_length=20)
    max_postulations = models.SmallIntegerField()
    max_active_cases = models.SmallIntegerField()
    price = models.FloatField()

    def __str__(self):
        return self.name
