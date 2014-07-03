import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from polls_remake.models import Poll


def create_poll(question = 'Who are you?', days = 0, hours = 0, choices = 3):
    """
    Factory method for creating polls with `question` and posted 
    `days` offset from now (positive for dates in the future,
    negative for dates in the past), and having `choices` number
    of choices
    """
    poll = Poll.objects.create(
        question = question, 
        pub_date = timezone.now() + datetime.timedelta(days = days, hours = hours)
    )

    for i in range(choices):
        poll.choice_set.create(choice_text = 'Choice No. %d' % (i + 1))

    return poll


class PollsMethodsTests(TestCase):

    def test_was_published_recently_with_future_poll(self):
        """
        was_published_recently should return False for polls whose
        pub_date is in the future.
        """
        poll = create_poll(days = 5)
        self.assertFalse(poll.was_published_recently())

    def test_was_published_recently_with_old_poll(self):
        """
        was_published_recently should return False for polls whose
        pub_date is older than one day.
        """
        poll = create_poll(days = -5)
        self.assertFalse(poll.was_published_recently())

    def test_was_published_recently_with_recent_poll(self):
        """
        was_published_recently should return True for polls whose
        pub_date is within the last day.
        """
        poll = create_poll(hours = -12)
        self.assertTrue(poll.was_published_recently())


class PollsIndexViewTests(TestCase):

    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls_remake:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_future_poll(self):
        """
        Polls with a pub_date in the future should not be displayed 
        in the index page.
        """
        create_poll(days = 5)
        response = self.client.get(reverse('polls_remake:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_past_poll(self):
        """
        Polls with a pub_date in the past should be displayed
        in the index page.
        """
        create_poll(days = -5)
        response = self.client.get(reverse('polls_remake:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Who are you?>'])


    def test_index_view_with_a_two_past_polls(self):
        """
        The index page may display multiple polls as long as their 
        pub_date values are in the past.
        """
        create_poll(question = 'Who is he?', days = -10)
        create_poll(question = 'Who is she?', days = -5)
        response = self.client.get(reverse('polls_remake:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Who is she?>', '<Poll: Who is he?>'])

    def test_index_view_with_a_future_poll_and_a_past_poll(self):
        """
        Even if both past polls and future polls exist, only the
        past polls should be displayed in the index page.
        """
        create_poll(question = 'Who is he?', days = 5)
        create_poll(question = 'Who is she?', days = -5)
        response = self.client.get(reverse('polls_remake:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Who is she?>'])

    def test_index_view_with_a_poll_having_no_choices(self):
        """
        Polls that have no choices should not be displayed in
        the index page regardless of their pub_date.
        """
        create_poll(days = -5, choices = 0)
        response = self.client.get(reverse('polls_remake:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_past_poll_having_some_choices(self):
        """
        Polls that have choices should be displayed in the index page
        given that their pub_date values are in the past.
        """
        create_poll(days = -5, choices = 5)
        response = self.client.get(reverse('polls_remake:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Who are you?>'])

    def test_index_view_with_a_future_poll_having_some_choices(self):
        """
        Polls that have choices should not be displayed in the index page
        if their pub_date values are in the future.
        """
        create_poll(days = 5, choices = 5)
        response = self.client.get(reverse('polls_remake:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])


class PollsDetailViewTests(TestCase):

    def test_detail_view_with_a_future_poll(self):
        """
        Detail page for a poll with a pub_date in the future should 
        return 404 Page Not Found.
        """
        poll = create_poll(days = 5)
        response = self.client.get(reverse('polls_remake:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll(self):
        """
        Detail page for a poll with a pub_date in the past should
        display the poll's question.
        """
        poll = create_poll(days = -5)
        response = self.client.get(reverse('polls_remake:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)

    def test_detail_view_with_a_poll_having_no_choices(self):
        """
        Detail page for a poll with no choices should return 
        404 Page Not Found, regardless of it's pub_date.
        """
        poll = create_poll(days = -5, choices = 0)
        response = self.client.get(reverse('polls_remake:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll_having_some_choices(self):
        """
        Detail page for a poll with choices should display the poll's
        question, as long as the poll's pub_date is in the past.
        """
        poll = create_poll(days = -5, choices = 5)
        response = self.client.get(reverse('polls_remake:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)

    def test_detail_view_with_a_future_poll_having_some_choices(self):
        """
        Detail page for a poll with some choices should return 
        404 Page Not Found if the poll's pub_date is in the future
        """
        poll = create_poll(days = 5, choices = 5)
        response = self.client.get(reverse('polls_remake:detail', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)


class PollsResultsViewTests(TestCase):

    def test_results_view_with_a_future_poll(self):
        """
        Results page for a poll with a pub_date in the future should 
        return 404 Page Not Found.
        """
        poll = create_poll(days = 5)
        response = self.client.get(reverse('polls_remake:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_poll(self):
        """
        Results page for a poll with a pub_date in the past should
        display the poll's question.
        """
        poll = create_poll(days = -5)
        response = self.client.get(reverse('polls_remake:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)

    def test_results_view_with_a_poll_having_no_choices(self):
        """
        Results page for a poll with no choices should return 
        404 Page Not Found, regardless of it's pub_date.
        """
        poll = create_poll(days = -5, choices = 0)
        response = self.client.get(reverse('polls_remake:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_a_past_poll_having_some_choices(self):
        """
        Results page for a poll with choices should display the poll's
        question, as long as the poll's pub_date is in the past.
        """
        poll = create_poll(days = -5, choices = 5)
        response = self.client.get(reverse('polls_remake:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll.question)

    def test_results_view_with_a_future_poll_having_some_choices(self):
        """
        Results page for a poll with some choices should return 
        404 Page Not Found if the poll's pub_date is in the future
        """
        poll = create_poll(days = 5, choices = 5)
        response = self.client.get(reverse('polls_remake:results', args = (poll.id,)))
        self.assertEqual(response.status_code, 404)