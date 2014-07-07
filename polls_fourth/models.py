import datetime

from django.db import models
from django.utils import timezone


class Poll(models.Model):
    question = models.CharField(max_length = 100)
    pub_date = models.DateTimeField('publication date')

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days = 1)

    def __unicode__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length = 100)
    votes = models.IntegerField(default = 0)

    def __unicode__(self):
        return self.choice_text
