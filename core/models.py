import datetime

from django.db import models
from django.utils import timezone
from django.db.models import Sum


class Question(models.Model):
    question_text = models.CharField(max_length=200, verbose_name="Question")
    pub_date = models.DateTimeField("date published")

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.question_text

    def get_total_votes(self):
        return self.choices.aggregate(Sum("votes", default=0))["votes__sum"]

    def was_published_recently(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        return yesterday <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.CharField(max_length=200, verbose_name="Choice")
    votes = models.PositiveIntegerField(default=0, verbose_name="Votes")

    class Meta:
        ordering = ["-votes"]

    def __str__(self):
        return self.choice_text

    def get_percentage(self):
        total_votes = self.question.get_total_votes()
        if not total_votes:
            return 0

        return int((self.votes / total_votes) * 100)
