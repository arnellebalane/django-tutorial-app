import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from polls_third_attempt.models import Poll


def create_poll(question = 'Who are you?', days = 0, hours = 0, choices = 3):
    poll = Poll.objects.create(
        question = question,
        pub_date = timezone.now() + datetime.timedelta(days = days, hours = hours)
    )

    for i in range(choices):
        poll.choice_set.create(choice_text = 'Choice No. %d' % (i + 1,))

    return poll


class PollsMethodsTests(TestCase):

    def test_was_published_recently_with_future_poll(self):
        poll = create_poll(days = 5)
        self.assertFalse(poll.was_published_recently())

    def test_was_published_recently_with_past_poll(self):
        poll = create_poll(days = -5)
        self.assertFalse(poll.was_published_recently())

    def test_was_published_recently_with_recent_poll(self):
        poll = create_poll(hours = -6)
        self.assertTrue(poll.was_published_recently())


class PollsIndexViewTests(TestCase):

    def test_index_view_with_no_polls(self):
        response = self.client.get(reverse('polls_third_attempt:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_future_poll(self):
        create_poll(days = 5)
        response = self.client.get(reverse('polls_third_attempt:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_past_poll(self):
        poll = create_poll(days = -5)
        response = self.client.get(reverse('polls_third_attempt:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: %s>' % poll.question])

    def test_index_view_with_a_future_poll_and_a_past_poll(self):
        future_poll = create_poll(question = 'Who is he?', days = 5)
        past_poll = create_poll(question = 'Who is she?', days = -5)
        response = self.client.get(reverse('polls_third_attempt:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: %s>' % past_poll.question])

    def test_index_view_with_two_past_polls(self):
        first_poll = create_poll(question = 'Who is he?', days = -10)
        second_poll = create_poll(question = 'Who is she?', days = -5)
        response = self.client.get(reverse('polls_third_attempt:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: %s>' % second_poll, '<Poll: %s>' % first_poll])

    def test_index_view_with_a_poll_having_no_choices(self):
        create_poll(days = -5, choices = 0)
        response = self.client.get(reverse('polls_third_attempt:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_future_poll_having_some_choices(self):
        create_poll(days = 5, choices = 5)
        response = self.client.get(reverse('polls_third_attempt:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_past_poll_having_some_choices(self):
        poll = create_poll(days = -5, choices = 5)
        response = self.client.get(reverse('polls_third_attempt:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: %s>' % poll.question])


class PollsDetailViewTests(TestCase):

    def test_detail_view_with_a_future_poll(self):
        poll = create_poll(days = 5)
        response = self.client.get(reverse('polls_third_attempt:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll(self):
        poll = create_poll(days = -5)
        response = self.client.get(reverse('polls_third_attempt:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)

    def test_detail_view_with_a_poll_having_no_choices(self):
        poll = create_poll(days = -5, choices = 0)
        response = self.client.get(reverse('polls_third_attempt:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_future_poll_having_some_choices(self):
        poll = create_poll(days = 5, choices = 5)
        response = self.client.get(reverse('polls_third_attempt:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll_having_some_choices(self):
        poll = create_poll(days = -5, choices = 5)
        response = self.client.get(reverse('polls_third_attempt:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)


class PollsResultsViewTests(TestCase):

    def test_results_view_with_a_future_poll(self):
        poll = create_poll(days = 5)
        response = self.client.get(reverse('polls_third_attempt:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_poll(self):
        poll = create_poll(days = -5)
        response = self.client.get(reverse('polls_third_attempt:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)

    def test_results_view_with_a_poll_having_no_choices(self):
        poll = create_poll(days = -5, choices = 0)
        response = self.client.get(reverse('polls_third_attempt:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_future_poll_having_some_choices(self):
        poll = create_poll(days = 5, choices = 5)
        response = self.client.get(reverse('polls_third_attempt:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_poll_having_some_choices(self):
        poll = create_poll(days = -5, choices = 5)
        response = self.client.get(reverse('polls_third_attempt:results', args = (poll.id,)))