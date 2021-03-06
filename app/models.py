from django.db import models


# Create your models here.
class Room(models.Model):
    room_id = models.CharField(max_length=30, db_index=True)
    has_started = models.BooleanField(default=False)
    game_round = models.IntegerField(default=0)
    users = models.CharField(max_length=8000)
    publish_result = models.CharField(max_length=3000, default='')
    valentine = models.CharField(max_length=200, default='[]')
    guarded = models.CharField(max_length=100, default='{"now":"", "last":""}')
    lycan = models.CharField(max_length=600, default='{"lycan_choice": {}}')
    poison = models.CharField(max_length=400, default='{"poison": 3, "dead": "", "is_rescue": false}')
    elder_life = models.IntegerField(default=2)
    idiot_show = models.BooleanField(default=False)
    idiot_say = models.BooleanField(default=False)
    badge = models.CharField(max_length=100, default='')
    can_talk = models.BooleanField(default=True)
    talk_list = models.CharField(max_length=2000, default='[]')
    finish_talk = models.CharField(max_length=2000, default='[]')
    vote_badge = models.CharField(max_length=2000, default='{}')
    vote_dead = models.CharField(max_length=2000, default='{}')

    def __unicode__(self):
        return self.room_id
