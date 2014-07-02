from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.db.models import Count

from polls.models import Choice, Poll


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        """
        Return the last five published polls.
        """
        polls = Poll.objects.annotate(choices_count = Count('choice'))
        polls = polls.filter(choices_count__gt = 0, pub_date__lte = timezone.now())
        return polls.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    template_name = 'polls/detail.html'
    model = Poll

    def get_queryset(self):
        """
        Excludes any polls whose pub_date are in the future.
        """
        polls = Poll.objects.annotate(choices_count = Count('choice'))
        return polls.filter(choices_count__gt = 0, pub_date__lte = timezone.now())


class ResultsView(generic.DetailView):
    template_name = 'polls/results.html'
    model = Poll

    def get_queryset(self):
        """
        Excludes any polls whose pub_date are in the future.
        """
        polls = Poll.objects.annotate(choices_count = Count('choice'))
        return polls.filter(choices_count__gt = 0, pub_date__lte = timezone.now())


def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk = poll_id)
    try: 
        choice = poll.choice_set.get(pk = request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'poll': poll,
            'error_message': "You didn't select a choice.",
        })
    else: 
        choice.votes += 1
        choice.save()
        return HttpResponseRedirect(reverse('polls:results', args = (poll.id,)))