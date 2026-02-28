from django.db import models
from django.db.models import Sum


class Question(models.Model):
    question_text = models.CharField(max_length=200, verbose_name="Question")
    pub_date = models.DateTimeField("date published")

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.question_text

    def get_total_votes(self):
        return self.choice_set.aggregate(Sum("votes", default=0))["votes__sum"]


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
            return "0%"

        return f"{int((self.votes / total_votes) * 100)}%"
