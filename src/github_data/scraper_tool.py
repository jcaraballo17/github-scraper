import logging
import math
import itertools
from logging import Logger
from typing import List, Optional, Tuple, Final

from fastcore.net import HTTP4xxClientError
from ghapi.core import GhApi
from fastcore.foundation import L as fastlist
from rest_framework.serializers import ModelSerializer

from github_data.exceptions import RateLimitExceededError
from github_data.models import GithubUser, GithubRepository
from github_data.serializers import GithubUserSerializer, GithubRepositorySerializer

logger: Logger = logging.getLogger(__name__)


class Scraper:
    MIN_PAGE_SIZE: Final[int] = 1
    MAX_PAGE_SIZE: Final[int] = 100
    DEFAULT_USER_PAGE_SIZE: Final[int] = 50
    DEFAULT_REPOSITORY_PAGE_SIZE: Final[int] = 30
    DEFAULT_NUMBER_OF_REPOSITORIES: Final[int] = 0
    DEFAULT_NUMBER_OF_USERS: Final[int] = 0
    NO_REPOSITORIES: Final[int] = 0
    NO_USERS: Final[int] = 0

    def __init__(self, *, token: Optional[str] = None,
                 users_page_size: int = DEFAULT_USER_PAGE_SIZE,
                 repositories_page_size: int = DEFAULT_REPOSITORY_PAGE_SIZE):
        """
        Initializes a GitHub Scraper with a determined page size for users and repositories.
        :param token: Github OAuth token to get a better rate limit
        :param users_page_size: The amount of users each github users api call will fetch. max: 100
        :param repositories_page_size: The amount of repositories each github repositories api call will fetch. max: 100
        """
        self.api: GhApi = GhApi(token=token)
        self.repositories_processed: int = 0
        self.users_processed: int = 0
        self.repositories_added: int = 0
        self.users_added: int = 0
        # Set bound for the page sizes to the minimum and the maximum values
        self.users_page_size: int = max(min(self.MAX_PAGE_SIZE, users_page_size), self.MIN_PAGE_SIZE)
        self.repositories_page_size: int = max(min(self.MAX_PAGE_SIZE, repositories_page_size), self.MIN_PAGE_SIZE)
        logger.debug(f'scrapper instance created with token: {token}.')

    def scrape_individual_users(self, usernames: List[str], *,
                                number_of_repositories: int = DEFAULT_NUMBER_OF_REPOSITORIES) -> None:
        """
        Scrapes a list of users and their repositories from the GitHub API.
        :param usernames: The list of usernames to scrape
        :param number_of_repositories: The number of repositories to be scraped for each user, 0 means all repositories
        :return:
        """

        # set bound for the number of users and repositories, set to the default 0 (all) if it's negative.
        number_of_repositories = max(number_of_repositories, self.DEFAULT_NUMBER_OF_REPOSITORIES)

        for username in usernames:
            logger.info(f'- scraping user {username}')
            try:
                user_data: fastlist = self.api.users.get_by_username(username)
            except HTTP4xxClientError as error:
                # Raise rate limit exceeded error.
                raise RateLimitExceededError(
                    error.url, error.code, 'Rate Limit Exceeded',
                    error.headers, error.fp
                )

            self.users_added += create_user(user_data)
            self.users_processed += 1
            try:
                self.scrape_user_repositories(username, number_of_repositories=number_of_repositories)
            except HTTP4xxClientError as error:
                # Raise rate limit exceeded error.
                raise RateLimitExceededError(
                    error.url, error.code, 'Rate Limit Exceeded',
                    error.headers, error.fp
                )

    def scrape_users(self, *, since: int = 0,
                     number_of_users: int = DEFAULT_NUMBER_OF_USERS,
                     number_of_repositories: int = DEFAULT_NUMBER_OF_REPOSITORIES) -> None:
        """
        Scrapes a determined quantity of users and their repositories from the GitHub API.
        :param since: The starting ID from where the number of users specified will be fetched
        :param number_of_users: The number of users to be scraped from the GitHub API,
        0 means all users. min: 0
        :param number_of_repositories: The number of repositories to be scraped for each User,
        0 means all repositories. min: 0
        :return:
        """

        # bound the number of users and repositories, set to the default 0 (all) if it's less than that.
        number_of_users = max(number_of_users, self.DEFAULT_NUMBER_OF_USERS)
        number_of_repositories = max(number_of_repositories, self.DEFAULT_NUMBER_OF_REPOSITORIES)
        logger.info(f'- scraping {number_of_users} user(s) and {number_of_repositories} repo(s) starting at id {since}')

        pages, remaining_count, page_size = self.calculate_user_paging(number_of_users)
        logger.debug(f'- scraping {pages} page(s) of {page_size} user(s) and one page of {remaining_count} user(s)')
        parse_remaining: bool = True

        for page_count in itertools.count(1):
            try:
                user_list: fastlist = self.api.users.list(since, per_page=page_size)
            except HTTP4xxClientError as error:
                raise RateLimitExceededError(
                    error.url, error.code, 'Rate Limit Exceeded',
                    error.headers, error.fp, last_id=since
                )
            logger.debug(f'- fetched {len(user_list)} user(s) in page #{page_count}')
            since: int = self.parse_users_list(user_list, number_of_repositories)

            # stop if reached page limit, or if there are no more users to get
            if pages and page_count >= pages or len(user_list) < page_size:
                parse_remaining = len(user_list) == page_size
                break

        if remaining_count and parse_remaining and since is not None:
            remaining_users: fastlist = self.api.users.list(since, per_page=remaining_count)
            self.parse_users_list(remaining_users, number_of_repositories)

    def parse_users_list(self, users: fastlist, number_of_repositories: int) -> Optional[int]:
        """
        Inserts all users from a list of user data into the database, and scrapes repository data for each user.
        :param users: The list containing user data
        :param number_of_repositories: The number of repositories to scrape for each User
        :return: The ID of the last user parsed. Returns `None` if the list is empty
        """
        last_user_id: Optional[int] = None
        for user in users:
            logger.info(f'- scraping user {user.login}')
            self.users_added += create_user(user)
            self.users_processed += 1

            try:
                self.scrape_user_repositories(user.login, number_of_repositories=number_of_repositories)
            except HTTP4xxClientError as error:
                raise RateLimitExceededError(
                    error.url, error.code, 'Rate Limit Exceeded',
                    error.headers, error.fp, last_id=last_user_id
                )
            last_user_id = user.id
        return last_user_id

    def scrape_user_repositories(self, username: str, *, number_of_repositories: int) -> None:
        """
        Scrapes a determined quantity of User Repositories from the GitHub Api.
        :param username: The username of the GitHub User to scrape Repositories from
        :param number_of_repositories: The number of repositories to be scraped, 0 means all repositories
        :return:
        """
        pages, page_size = self.calculate_repository_paging(number_of_repositories)
        logger.debug(f'-- scraping {pages} page(s) of {page_size} repositories for user {username}')

        for page in itertools.count(1):
            repository_list: fastlist = self.api.repos.list_for_user(username, page=page, per_page=page_size)
            logger.debug(f'-- fetched {len(repository_list)} repositories in page {page}')
            self.parse_repositories_list(repository_list)

            # stop if reached page limit, or if there are no more repositories to get
            if pages and page >= pages or len(repository_list) < page_size:
                break

    def parse_repositories_list(self, repositories: fastlist) -> None:
        """
        Inserts all repositories from a list of repository data into the database
        :param repositories: The list containing repository data
        :return:
        """
        for repository in repositories:
            logger.info(f'-- scraping repository {repository.full_name}')
            self.repositories_added += create_repository(repository)
            self.repositories_processed += 1

    def calculate_user_paging(self, number_of_users: int) -> Tuple[int, int, int]:
        """
        Calculates paging information to be used to get the User data from the GitHub Api.
        :param number_of_users: The number of users to paginate
        :return: The number of pages, any remaining quantity of users, and the page size
        """

        # bound the number of users, set to the default 0 (all) if it's negative.
        number_of_users = max(number_of_users, self.DEFAULT_NUMBER_OF_USERS)

        # no calculation needed if we want all repositories
        # return 0 pages, 0 remainder, and the same page size
        if number_of_users == 0:
            return self.NO_USERS, self.NO_USERS, self.repositories_page_size

        page_size: int = self.users_page_size
        pages, remaining_count = divmod(number_of_users, page_size)

        # if the number of users is less than the page size,
        # make it so that there's only one page with that particular size
        if number_of_users < page_size:
            page_size = remaining_count
            remaining_count = 0
            pages = 1

        return pages, remaining_count, page_size

    def calculate_repository_paging(self, number_of_repositories: int) -> Tuple[int, int]:
        """
        Calculates paging information to be used to get the Repository data for each User from the GitHub Api.
        :param number_of_repositories: The number of repositories to paginate
        :return: The number of pages and the page size to get the desired amount of repositories
        """

        # bound the number of repositories, set to the default 0 (all) if it's negative.
        number_of_repositories = max(number_of_repositories, self.DEFAULT_NUMBER_OF_REPOSITORIES)

        # no calculation needed if we want all repositories
        if number_of_repositories == 0:
            return self.NO_REPOSITORIES, self.repositories_page_size

        # if the number of repositories has any remainder after dividing by the page size
        # and the user has a bigger total number of repositories, the pagination will give you a whole extra page
        # with more repositories than what was specified in `number_of_repositories`.
        # so.... let's find the factors of `number_of_repositories`
        # and use the closest one to `self.repositories_page_size` as the page size.
        # i brought this on myself.

        factors: List[int] = [
            n for n in range(1, number_of_repositories + 1)
            if number_of_repositories % n == 0
        ]

        page_size: int = min(factors, key=lambda x: abs(x - self.repositories_page_size))
        pages: int = math.ceil(number_of_repositories / page_size)

        # if the number of repositories is less than the page size,
        # make it so that there's only one page with that particular size
        if 0 < number_of_repositories < page_size:
            page_size = number_of_repositories

        return pages, page_size


def create_user(user_data: fastlist) -> bool:
    """
    Helper function that uses the Django Rest Framework ModelSerializer
    to validate and insert a GithubUser object into the database.
    :param user_data: Github User data
    :return: Whether or not the user was inserted into the database
    """
    user: Optional[GithubUser] = None
    serializer: ModelSerializer = GithubUserSerializer(data=user_data)
    if serializer.is_valid():
        user = serializer.save()
        logger.debug(f'- user {user.login} added to the database.')
    return user is not None


def create_repository(repository_data: fastlist) -> bool:
    """
    Helper function that uses the Django Rest Framework ModelSerializer
    to validate and insert a GithubRepository object into the database.
    :param repository_data: Github Repository data
    :return: Whether or not the repository was inserted into the database
    """
    repository: Optional[GithubRepository] = None
    serializer: ModelSerializer = GithubRepositorySerializer(data=repository_data)
    if serializer.is_valid():
        repository = serializer.save()
        logger.debug(f'-- repository {repository.full_name} added to the database.')
    return repository is not None
