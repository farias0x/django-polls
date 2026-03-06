from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import generic
from .models import Question, Choice


class IndexView(generic.ListView):
    model = Question
    template_name = "core/index.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


class DetailView(generic.DetailView):
    model = Question
    template_name = "core/detail.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "core/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choices.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        context = {"question": question, "error_message": "You didn't select a choice."}
        return render(request, "core/detail.html", context)
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("core:results", args=(question.id,)))
