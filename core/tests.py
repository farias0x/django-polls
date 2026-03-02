import datetime
from django.utils import timezone
from django.test import TestCase
from .models import Question


def create_question(question_text="", days=0):
    """Helper function to create a Question for testing purposes."""
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelsTests(TestCase):
    """Tests for the Question model and its methods."""

    def test_get_total_votes_with_no_choices(self):
        """get_total_votes() returns 0 when the question has no choices."""
        question = create_question()
        self.assertEqual(question.get_total_votes(), 0)

    def test_get_total_votes_with_multiple_choices(self):
        """get_total_votes() returns the sum of votes across all choices."""
        question = Question.objects.create(
            question_text="Multiple choices?", pub_date=timezone.now()
        )
        question.choices.create(choice_text="A", votes=10)
        question.choices.create(choice_text="B", votes=2)
        question.choices.create(choice_text="C", votes=0)
        self.assertEqual(question.get_total_votes(), 12)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for questions published within the last day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions published more than 1 day ago."""
        time = timezone.now() - datetime.timedelta(days=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions with future pub_date."""
        time = timezone.now() + datetime.timedelta(seconds=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
