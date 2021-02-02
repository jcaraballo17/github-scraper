from django.test import TestCase

from github_data.models import GithubUser, GithubRepository


class TestGithubUser(TestCase):
    def test_string_representation(self):
        user = GithubUser(id=777, login='isthisarealuser', url='https://api.github.com/users/isthisarealuser')
        self.assertEqual(str(user), user.login)


class TestGithubRepository(TestCase):
    def test_string_representation(self):
        user = GithubUser(id=777, login='isthisarealuser', url='https://api.github.com/users/isthisarealuser')
        repository = GithubRepository(
            id=888, owner=user, full_name='isthisarealuser/head-scratcher', name='head-scratcher',
            description='', url='https://api.github.com/users/isthisarealuser/head-scratcher'
        )
        self.assertEqual(str(repository), f'{user.login}/{repository.name}')
