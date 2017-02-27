import pandas as pd
from django.db import models

class Client(models.Model):
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    name = models.CharField(max_length=200, unique=True)
    VAT_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    rate = models.FloatField()
    togglId = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class TimeEntryDFManager(models.Manager):
    def get_queryset_df(self, *args, **kwargs):
        df = pd.DataFrame(list(super(TimeEntryDFManager, self).get_queryset().filter(*args, **kwargs).values()))
        return df

class TimeEntry(models.Model):
    billable = models.BooleanField(default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    start = models.DateTimeField()
    duration = models.FloatField()
    duration_unit = models.CharField(choices=(('days', 'days'), ('hours', 'hours'), ('minutes', 'minutes')), default='hours', max_length=10)
    togglId = models.CharField(max_length=20, unique=True)

    objects = TimeEntryDFManager()

    def __str__(self):
        return '{0} : {1}'.format(self.project, self.start.isoformat())


class Invoice(models.Model):
    number = models.IntegerField(unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    VAT_percentage = models.IntegerField(default=21)

    def __str__(self):
        return self.number