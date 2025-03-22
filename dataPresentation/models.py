from django.db import models

# Create your models here.

from django.db import models

class GPAData(models.Model):
    year = models.CharField(max_length=4)
    term = models.CharField(max_length=10)
    college = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    gpa = models.FloatField()

    def __str__(self):
        return f"{self.year} - {self.term} - {self.college} - {self.course} - {self.gpa}"