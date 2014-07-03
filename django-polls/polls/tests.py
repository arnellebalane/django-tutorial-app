import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from polls.models import Poll


def create_poll(question, days, choices = 3):
    """
    Creates a poll with the given `question` published the given number of
    `days` offset to now (negative for polls published in the past, positive
    for polls that have yet to be published) and with `choices` number of 
    choices.
    """
    poll = Poll.objects.create(
        question = question, 
        pub_date = timezone.now() + datetime.timedelta(days = days)
    )

    for i in range(choices):
        poll.choice_set.create(choice_text = "Choice No. %d" % i)

    return poll


class PollMethodTests(TestCase):

    def test_was_published_recently_with_future_poll(self):
        """
        was_published_recently should return False for polls whose
        pub_date is in the future
        """
        poll = Poll(pub_date = timezone.now() + datetime.timedelta(days = 30))
        self.assertEqual(poll.was_published_recently(), False)

    def test_was_published_recently_with_old_poll(self):
        """
        was_published_recently should return False for polls whose
        pub_date is older that 1 days
        """
        poll = Poll(pub_date = timezone.now() - datetime.timedelta(days = 30))
        self.assertEqual(poll.was_published_recently(), False)

    def test_was_published_recently_with_recent_poll(self):
        """
        was_published_recently should return True for polls whose
        pub_date is within the last day
        """
        poll = Poll(pub_date = timezone.now() - datetime.timedelta(hours = 6))
        self.assertEqual(poll.was_published_recently(), True)


class PollIndexViewTests(TestCase):

    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be displayed on the index page.
        """
        create_poll(question = 'Who are you?', days = -5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Who are you?>'])

    def test_index_view_with_a_future_poll(self):
        """
        Polls with a pub_date in the future should not be displayed on the index page.
        """
        create_poll(question = 'Who are you?', days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future polls exist, only past polls should be displayed.
        """
        create_poll(question = 'Who is he?', days = -5)
        create_poll(question = 'Who is she?', days = 5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Who is he?>'])

    def test_index_view_with_two_past_polls(self):
        """
        The polls index page should display all past polls.
        """
        create_poll(question = 'Who is he?', days = -10)
        create_poll(question = 'Who is she?', days = -5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Who is she?>', '<Poll: Who is he?>'])

    def test_index_view_a_poll_having_no_choices(self):
        """
        Polls with no choices should not be displayed on the index page.
        """
        create_poll(question = 'Who are you?', days = -5, choices = 0)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_poll_having_some_choices(self):
        """
        Polls with choices should be displayed on the index page.
        """
        create_poll(question = 'Who are you?', days = -5, choices = 5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Who are you?>'])


class PollDetailViewTests(TestCase):

    def test_detail_view_with_a_future_poll(self):
        """
        The detail view of a poll with a pub_date in the future should
        return a 404 Page Not Found.
        """
        poll = create_poll(question = 'Who are you?', days = 5)
        response = self.client.get(reverse('polls:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll(self):
        """
        The detail view of a poll with a pub_date in the past should
        display the poll's question.
        """
        poll = create_poll(question = 'Who are you?', days = -5)
        response = self.client.get(reverse('polls:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)

    def test_detail_view_with_a_poll_having_no_choices(self):
        """
        The detail view of a poll with no choices should return 
        a 404 Page Not Found.
        """
        poll = create_poll(question = 'Who are you?', days = -5, choices = 0)
        response = self.client.get(reverse('polls:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_poll_having_some_choices(self):
        """
        The detail view of a poll with choices should
        display the poll's question.
        """
        poll = create_poll(question = 'Who are you?', days = -5, choices = 5)
        response = self.client.get(reverse('polls:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)


class PollResultsViewTests(TestCase):

    def test_results_view_with_a_future_poll(self):
        """
        The results view of a poll with a pub_date in the future should
        return a 404 Page Not Found.
        """
        poll = create_poll(question = 'Who are you?', days = 5)
        response = self.client.get(reverse('polls:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_poll(self):
        """
        The results view of a poll with a pub_date in the future should
        display the poll's results.
        """
        poll = create_poll(question = 'Who are you?', days = -5)
        response = self.client.get(reverse('polls:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)

    def test_results_view_with_a_poll_having_no_choices(self):
        """
        The results view of a poll with no choices should return
        a 404 Page Not Found.
        """
        poll = create_poll(question = 'Who are you?', days = -5, choices = 0)
        response = self.client.get(reverse('polls:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_poll_having_some_choices(self):
        """
        The results view of a poll with some choices should
        display the poll's results.
        """
        poll = create_poll(question = 'Who are you?', days = -5, choices = 5)
        response = self.client.get(reverse('polls:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)