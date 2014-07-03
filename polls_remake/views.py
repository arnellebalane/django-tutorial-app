from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.db.models import Count

from polls_remake.models import Poll, Choice


class IndexView(generic.ListView):
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        polls = Poll.objects.annotate(choices_count = Count('choice'))
        polls = polls.filter(choices_count__gt = 0, pub_date__lte = timezone.now())
        return polls.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):

    def get_queryset(self):
        polls = Poll.objects.annotate(choices_count = Count('choice'))
        return polls.filter(choices_count__gt = 0, pub_date__lte = timezone.now())


class ResultsView(generic.DetailView):
    template_name = 'polls_remake/poll_results.html'

    def get_queryset(self):
        polls = Poll.objects.annotate(choices_count = Count('choice'))
        return polls.filter(choices_count__gt = 0, pub_date__lte = timezone.now())


def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk = poll_id)
    try:
        choice = poll.choice_set.get(pk = request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls_remake/poll_detail.html', {
            'poll': poll,
            'error_message': 'You did not select a choice.',
        })
    else:
        choice.votes += 1
        choice.save()
        return HttpResponseRedirect(reverse('polls_remake:results', args = (poll.id,)))