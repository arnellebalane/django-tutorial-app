from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.db.models import Count

from polls_third_attempt.models import Poll, Choice


class IndexView(generic.ListView):
    template_name = 'polls_third_attempt/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        polls = Poll.objects.annotate(choices_count = Count('choice'))
        polls = polls.filter(choices_count__gt = 0, pub_date__lte = timezone.now())
        return polls.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    template_name = 'polls_third_attempt/detail.html'

    def get_queryset(self):
        polls = Poll.objects.annotate(choices_count = Count('choice'))
        return polls.filter(choices_count__gt = 0, pub_date__lte = timezone.now())


class ResultsView(generic.DetailView):
    template_name = 'polls_third_attempt/results.html'

    def get_queryset(self):
        polls = Poll.objects.annotate(choices_count = Count('choice'))
        return polls.filter(choices_count__gt = 0, pub_date__lte = timezone.now())


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
        return HttpResponseRedirect(reverse('polls_third_attempt:results', args = (poll.id,)))