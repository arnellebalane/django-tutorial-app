from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import generic

from polls_third_attempt.models import Poll, Choice


class IndexView(generic.ListView):
    model = Poll
    template_name = 'polls_third_attempt/index.html'
    context_object_name = 'latest_poll_list'


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls_third_attempt/detail.html'


class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls_third_attempt/results.html'


def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk = poll_id)
    try:
        choice = poll.choice_set.get(pk = request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        context = {
            'poll': poll,
            'error_message': 'You did not select a choice.'
        }
        return render(request, 'polls_third_attempt/detail.html', context)
    else:
        choice.votes += 1
        choice.save()
        return HttpResponseRedirect('/polls/%d/results' % poll.id)