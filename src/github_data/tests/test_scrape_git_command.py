from django.core.management import call_command
from django.test import TestCase

from github_data.exceptions import RateLimitExceededError
from github_data.models import GithubUser, GithubRepository


class ScrapeCommandTestCase(TestCase):
    def test_2_specific_users(self):
        # test user argument
        args = ['jcaraballo17', 'Maurier']
        try:
            call_command('scrape_git', *args)
        except RateLimitExceededError:
            self.skipTest('Unable to complete test: Github rate limit exceeded! Try again later.')

        self.assertTrue(GithubUser.objects.filter(login='jcaraballo17').exists())
        self.assertTrue(GithubUser.objects.filter(login='Maurier').exists())
        self.assertEqual(GithubRepository.objects.filter(owner__login='jcaraballo17').count(), 2)
        self.assertEqual(GithubRepository.objects.filter(owner__login='Maurier').count(), 3)

    def test_1_specific_user_with_1_repository(self):
        # test user argument with repositories option
        args = ['jcaraballo17']
        options = {'repositories': 1}
        try:
            call_command('scrape_git', *args, **options)
        except RateLimitExceededError:
            self.skipTest('Unable to complete test: Github rate limit exceeded! Try again later.')

        self.assertTrue(GithubUser.objects.filter(login='jcaraballo17').exists())
        self.assertEqual(GithubRepository.objects.filter(owner__login='jcaraballo17').count(), 1)

    def test_first_5_users_1_repository(self):
        # try users and repositories options
        args = []
        options = {'users': 5, 'repositories': 1}

        try:
            call_command('scrape_git', *args, **options)
        except RateLimitExceededError:
            self.skipTest('Unable to complete test: Github rate limit exceeded! Try again later.')

        self.assertEqual(GithubUser.objects.count(), 5)
        self.assertEqual(GithubRepository.objects.count(), 5)

    def test_2_users_all_repositories_since_id(self):
        # try since and users options
        args = []
        options = {'since': 125, 'users': 2}

        try:
            call_command('scrape_git', *args, **options)
        except RateLimitExceededError:
            self.skipTest('Unable to complete test: Github rate limit exceeded! Try again later.')

        self.assertEqual(GithubUser.objects.count(), 2)
        self.assertEqual(GithubRepository.objects.count(), 66)
