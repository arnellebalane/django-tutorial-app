from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import generic

from polls_fourth.models import Poll, Choice


class IndexView(generic.ListView):

    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte = timezone.now())


def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk = poll_id)
    try:
        choice = poll.choice_set.get(pk = request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        pass
    else:
        choice.votes += 1
        choice.save()
        return redirect('polls:index')
