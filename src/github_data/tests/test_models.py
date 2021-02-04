from django.test import TestCase

from github_data.models import GithubUser, GithubRepository


class TestGithubUser(TestCase):
    def setUp(self):
        self.user: GithubUser = GithubUser(id=777, login='realuser', url='https://api.github.com/users/realuser')

    def test_string_representation(self):
        self.assertEqual(str(self.user), self.user.login)


class TestGithubRepository(TestCase):
    def setUp(self):
        self.user: GithubUser = GithubUser(id=777, login='realuser', url='https://api.github.com/users/realuser')
        self.repository: GithubRepository = GithubRepository(
            id=888, owner=self.user, full_name='realuser/head-scratcher', name='head-scratcher',
            description='', url='https://api.github.com/users/realuser/head-scratcher'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.repository), f'{self.user.login}/{self.repository.name}')
