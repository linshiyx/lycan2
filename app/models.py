from django.db import models
from django.utils import timezone

# Create your models here.
class Room(models.Model):
    room_id = models.CharField(max_length=20, db_index=True)
    game_round = models.IntegerField(default=0)
    users = models.CharField(max_length=2000)
    valentine = models.CharField(max_length=50, default='[]')
    guarded = models.CharField(max_length=20, default='')
    lycan = models.CharField(max_length=200, default='{"lycan_choice": {}}')
    poison = models.CharField(max_length=200, default='{"poison": 3}')
    badge = models.CharField(max_length=20, default='')
    can_talk = models.BooleanField(default=False)
    talk_list = models.CharField(max_length=500, default='[]')
    finish_talk = models.CharField(max_length=500, default='[]')
    vote_badge = models.CharField(max_length=500, default='{}')
    vote_dead = models.CharField(max_length=500, default='{}')

    def __unicode__(self):
        return self.room_id