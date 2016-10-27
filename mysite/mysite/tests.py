from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

TEST_USER = 'tester'
TEST_PASSWORD = 'tester'


class QuestionViewTests(TestCase):
    def setUp(self):
        super(QuestionViewTests, self).setUp()
        # create user
        user = User.objects.create_user('tester', 'tester@tester.com', 'tester')

    def test_root_api(self):
        """
        Testing that root api returns expected values.
        """
        self.client.login(**{'username': TEST_USER, 'password': TEST_PASSWORD})
        api_contract_l = settings.ROOT_API_CONTRACT
        response = self.client.get(reverse('api-root'))
        status_code = response.status_code
        resp_d = response.json()
        self.assertTrue(status_code == 200, 'Request failed with status code {0} message {1}'.format(status_code,
                                                                                                     str(resp_d)))
        self.assertTrue(list(api_contract_l) == resp_d.keys(), 'Expected {0} received {1}'.format(api_contract_l,
                                                                                                  resp_d.keys()))
