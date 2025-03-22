from django.db import models

# Create your models here.

from django.db import models

class GPAData(models.Model):
    gpa_group = models.CharField(max_length=20)
    freshman_male = models.IntegerField()
    freshman_female = models.IntegerField()
    freshman_total = models.IntegerField()
    sophomore_male = models.IntegerField()
    sophomore_female = models.IntegerField()
    sophomore_total = models.IntegerField()
    junior_male = models.IntegerField()
    junior_female = models.IntegerField()
    junior_total = models.IntegerField()
    senior_male = models.IntegerField()
    senior_female = models.IntegerField()
    senior_total = models.IntegerField()

    def __str__(self):
        return self.gpa_group