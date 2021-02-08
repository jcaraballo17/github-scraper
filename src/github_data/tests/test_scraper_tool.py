from typing import List
from django.test import TestCase

from github_data.exceptions import RateLimitExceededError
from github_data.models import GithubUser, GithubRepository
from github_data.scraper_tool import Scraper


class ScraperPaginationTestCase(TestCase):
    """
    Tests for the User and Repository pagination methods of the Scraper tool.
    """
    def setUp(self) -> None:
        self.page_size_5_scraper: Scraper = Scraper(users_page_size=5, repositories_page_size=5)
        self.page_size_20_scraper: Scraper = Scraper(users_page_size=20, repositories_page_size=20)
        self.bounded_page_size_scraper: Scraper = Scraper(users_page_size=240, repositories_page_size=-50)

    def test_calculate_user_paging(self) -> None:
        # response is ({number of pages}, {remaining users}, {page size})
        # normal case with no remaining users
        self.assertTupleEqual(self.page_size_5_scraper.calculate_user_paging(25), (5, 0, 5))
        # number of users less than page size
        self.assertTupleEqual(self.page_size_5_scraper.calculate_user_paging(3), (1, 0, 3))
        # normal case with remaining users
        self.assertTupleEqual(self.page_size_20_scraper.calculate_user_paging(364), (18, 4, 20))
        # all users
        self.assertTupleEqual(self.page_size_20_scraper.calculate_user_paging(0), (0, 0, 20))

    def test_calculate_repository_paging(self) -> None:
        # response is ({number of pages}, {page size})
        # normal case with no extra page
        self.assertTupleEqual(self.page_size_5_scraper.calculate_repository_paging(40), (8, 5))
        # number of repositories less than page size
        self.assertTupleEqual(self.page_size_5_scraper.calculate_repository_paging(1), (1, 1))
        # normal case with adjusted page size
        self.assertTupleEqual(self.page_size_20_scraper.calculate_repository_paging(50), (2, 25))
        # all repositories
        self.assertTupleEqual(self.page_size_20_scraper.calculate_repository_paging(0), (0, 20))
        # requesting an invalid number of repositories (less than 0)
        self.assertTupleEqual(self.page_size_20_scraper.calculate_repository_paging(-1), (0, 20))

    def test_page_size_bounds(self) -> None:
        negative_paged_scraper: Scraper = Scraper(users_page_size=-15, repositories_page_size=-10)
        big_scraper: Scraper = Scraper(users_page_size=150, repositories_page_size=5000)

        # the negative page sizes default to the minimum
        self.assertEqual(negative_paged_scraper.users_page_size, Scraper.MIN_PAGE_SIZE)
        self.assertEqual(negative_paged_scraper.repositories_page_size, Scraper.MIN_PAGE_SIZE)

        # the page sizes that are greater than the max value default to the maximum
        self.assertEqual(big_scraper.users_page_size, Scraper.MAX_PAGE_SIZE)
        self.assertEqual(big_scraper.users_page_size, Scraper.MAX_PAGE_SIZE)


class TestScraper(TestCase):
    """
    Tests for the scraping methods of the Scraper tool.
    """
    def setUp(self) -> None:
        self.page_size_10_scraper: Scraper = Scraper(users_page_size=1, repositories_page_size=1)
        self.page_size_3_scraper: Scraper = Scraper(users_page_size=3, repositories_page_size=3)

    def test_scraping_individual_users(self) -> None:
        users: List[str] = ['jcaraballo17', 'Maurier']

        try:
            self.page_size_10_scraper.scrape_individual_users(users, number_of_repositories=1)
        except RateLimitExceededError:
            self.skipTest('Unable to complete test: Github rate limit exceeded! Try again later.')

        self.assertTrue(GithubUser.objects.filter(login='jcaraballo17').exists())
        self.assertTrue(GithubUser.objects.filter(login='Maurier').exists())
        self.assertEqual(GithubRepository.objects.filter(owner__login='jcaraballo17').count(), 1)
        self.assertEqual(GithubRepository.objects.filter(owner__login='Maurier').count(), 1)
        self.assertEqual(self.page_size_10_scraper.users_processed, 2)
        self.assertEqual(self.page_size_10_scraper.repositories_processed, 2)

    def test_scraping_2_users_2_repositories(self) -> None:
        starting_id: int = 4700504  # 4700505 has 2 repositories, 4700506 has 0 repositories

        try:
            self.page_size_3_scraper.scrape_users(since=starting_id, number_of_users=2, number_of_repositories=2)
        except RateLimitExceededError:
            self.skipTest('Unable to complete test: Github rate limit exceeded! Try again later.')

        self.assertTrue(GithubUser.objects.filter(id=4700505).exists())
        self.assertTrue(GithubUser.objects.filter(id=4700506).exists())
        self.assertEqual(GithubRepository.objects.filter(owner_id=4700505).count(), 2)
        self.assertEqual(GithubRepository.objects.filter(owner_id=4700506).count(), 0)
        self.assertEqual(self.page_size_3_scraper.users_processed, 2)
        self.assertEqual(self.page_size_3_scraper.repositories_processed, 2)

    def test_scraping_3_users_all_repositories(self) -> None:
        starting_id: int = 4721939
        # 4721940 sreeder 8 repositories
        # 4721941 scatterfull 0 repositories
        # 4721942 TeJay8 has 7 repositories

        try:
            self.page_size_3_scraper.scrape_users(since=starting_id, number_of_users=3, number_of_repositories=0)
        except RateLimitExceededError:
            self.skipTest('Unable to complete test: Github rate limit exceeded! Try again later.')

        self.assertTrue(GithubUser.objects.filter(id=4721940).exists())
        self.assertTrue(GithubUser.objects.filter(id=4721941).exists())
        self.assertTrue(GithubUser.objects.filter(id=4721942).exists())
        self.assertEqual(GithubRepository.objects.filter(owner_id=4721940).count(), 8)
        self.assertEqual(GithubRepository.objects.filter(owner_id=4721941).count(), 0)
        self.assertEqual(GithubRepository.objects.filter(owner_id=4721942).count(), 7)
        self.assertEqual(self.page_size_3_scraper.users_processed, 3)
        self.assertEqual(self.page_size_3_scraper.repositories_processed, 15)

    def test_scraping_1_existing_user_2_repositories(self) -> None:
        GithubUser.objects.create(id=4700505, login='jcaraballo17', url="https://api.github.com/users/jcaraballo17")
        try:
            self.page_size_10_scraper.scrape_individual_users(['jcaraballo17'], number_of_repositories=2)
        except RateLimitExceededError:
            self.skipTest('Unable to complete test: Github rate limit exceeded! Try again later.')
        self.assertEqual(GithubRepository.objects.filter(owner__login='jcaraballo17').count(), 2)
        self.assertEqual(self.page_size_10_scraper.users_added, 0)
        self.assertEqual(self.page_size_10_scraper.users_processed, 1)
        self.assertEqual(self.page_size_10_scraper.repositories_processed, 2)
