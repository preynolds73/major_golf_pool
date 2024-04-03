from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class Golfer(models.Model):
    name = models.CharField(max_length=100, default="deleteme")
    odds = models.IntegerField(default=500000)
    tier = models.IntegerField(default=0)
    place = models.IntegerField(default=404)
    cut = models.BooleanField(default=False)
    wd = models.BooleanField(default=False)
    thru = models.CharField(max_length=100, default="deleteme")
    ttl_score = models.IntegerField(default=404)
    today_score = models.IntegerField(default=404)
    r1_score = models.IntegerField(default=404)
    r2_score = models.IntegerField(default=404)
    r3_score = models.CharField(max_length=100, default="deleteme")
    r4_score = models.CharField(max_length=100, default="deleteme")

# Probably need to do some class inheritance here,
# but I'm trying to make this as flat as possible for the 1st run
class Team(models.Model):
    owner = models.CharField(max_length=100, default="deleteme")
    total_score = models.IntegerField(default=0)
    golfer = models.ManyToManyField(Golfer, related_name="team_golfer")

    def __str__(self):
        return self.owner

