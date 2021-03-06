import datetime
import json
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from .models import Question, Choice


def create_question(question_text, days):
    """
    Creates a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_choice(question_obj, text):
    """
    Creates a new choice for a question_object
    """
    choice = Choice.objects.create(question=question_obj, choice_text=text)
    return choice


class VoteTests(TestCase):
    def test_vote(self):
        """
        Tests that vote funtion can vote.
        """
        question = create_question(question_text="Vote question.", days=1)
        choice = create_choice(question, "Vote choice 1")
        url_params = {'question_id': question.id}
        data_d = {'choice': choice.id}
        expected_url = reverse('polls:results', kwargs={'pk': question.id})
        response = self.client.post(reverse('polls:vote', kwargs=url_params), data_d)
        self.assertRedirects(response, expected_url)

        # test bad choice
        data_d = {'choice': -42}
        response = self.client.post(reverse('polls:vote', kwargs=url_params), data_d)
        self.assertTrue(response.status_code == 200)


class ChoiceViewTests(TestCase):
    def test_choice_text(self):
        """
        Tests that a choice object returns choice_text attriburte
        """
        question = create_question(question_text="Choice question.", days=1)
        choice = create_choice(question, "Test Choice")
        self.assertTrue(str(choice) == "Test Choice")


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the
        index page.
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_was_published_recently(self):
        """
        Tests if was_published_recently funtion on model
        """
        q = create_question(question_text="Recent question 1.", days=0)
        self.assertTrue(q.was_published_recently(), "Failed to validate recently published")


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

