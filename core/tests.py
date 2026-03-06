import datetime
from django.utils import timezone
from django.test import TestCase
from .models import Question, Choice
from django.urls import reverse


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
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions with future pub_date."""
        time = timezone.now() + datetime.timedelta(seconds=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)


class ChoiceModelsTests(TestCase):
    def test_get_percentage_with_no_total_votes(self):
        """get_percentage() returns 0 when the question has no choices."""
        question = create_question()
        choice = Choice.objects.create(question=question, choice_text="A", votes=0)
        self.assertEqual(choice.get_percentage(), 0)

    def test_get_percentage_with_one_choice_without_vote(self):
        """get_percentage() returns 0 when this choice has no votes but other choices exist."""
        question = create_question()
        Choice.objects.create(question=question, choice_text="A", votes=7)
        choice = Choice.objects.create(question=question, choice_text="B", votes=0)
        self.assertEqual(choice.get_percentage(), 0)

    def test_get_percentage_with_one_choice_with_vote(self):
        """get_percentage() returns 100 when there's only one choice with votes."""
        choice = Choice.objects.create(
            question=create_question(), choice_text="", votes=7
        )
        self.assertEqual(choice.get_percentage(), 100)

    def test_get_percentage_with_multiple_choices_with_vote(self):
        """get_percentage() returns correct percentage when multiple choices have votes."""
        question = create_question()
        Choice.objects.create(question=question, choice_text="", votes=5)
        choice = Choice.objects.create(question=question, choice_text="", votes=1)
        self.assertEqual(choice.get_percentage(), 16)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("core:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls available.")
        self.assertQuerySetEqual(response.context["question_list"], [])

    def test_past_question(self):
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("core:index"))
        self.assertQuerySetEqual(
            response.context["question_list"],
            [question],
        )

    def test_future_question(self):
        create_question(question_text="Future question.", days=1)
        response = self.client.get(reverse("core:index"))
        self.assertContains(response, "No polls available")
        self.assertQuerySetEqual(response.context["question_list"], [])

    def test_future_question_and_past_question(self):
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("core:index"))
        self.assertQuerySetEqual(
            response.context["question_list"],
            [question],
        )

    def test_two_past_questions(self):
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("core:index"))
        self.assertQuerySetEqual(
            response.context["question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text="Future question.", days=4)
        url = reverse("core:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text="Past question.", days=-5)
        url = reverse("core:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
