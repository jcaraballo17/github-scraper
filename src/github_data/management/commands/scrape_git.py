import logging
import time

from logging import Logger
from typing import List, Optional, Dict, Any

from django.core.management import BaseCommand
from django.conf import settings

from github_data.exceptions import RateLimitExceededError
from github_data.scraper_tool import Scraper

logger: Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help: str = 'Scrapes GitHub User and Repository Data.'
    number_of_repositories: Optional[int] = None
    number_of_users: Optional[int] = None
    since: Optional[int] = None
    retry: bool = False

    def add_arguments(self, parser):
        parser.add_argument('user', nargs='*', type=str,
                            help='One or more usernames to scrape from the GitHub API.')
        parser.add_argument('--since', nargs='?', type=int, metavar='id',
                            help='A starting ID to scrape a range consecutive of users,')
        parser.add_argument('--users', nargs='?', type=int, metavar='number of users',
                            help='The number of users to scrape.')
        parser.add_argument('--repositories', nargs='?', type=int, metavar='number of repositories',
                            help='The number of repositories per users to scrape.')
        parser.add_argument('--retry', action='store_true',
                            help='If rate limit is reached, wait and continue scraping after the reset time has passed.')

    def handle(self, *args, **options):
        # get all arguments to pass on to the scraper
        self.retry = options.get('retry')
        self.since = options.get('since')
        self.number_of_users = options.get('users')
        self.number_of_repositories = options.get('repositories')

        # if there are individual users, get em.
        if len(options.get('user')):
            logger.info('- scraping individual users')
            self.handle_individual_users(options.get('user'))
            return

        logger.info('- scraping a range of users')
        self.handle_users_range()

    def handle_individual_users(self, user_list: List[str], scraper: Scraper = None) -> None:
        kwargs: Dict[str, Any] = {}
        if self.number_of_repositories is not None:
            kwargs['number_of_repositories'] = self.number_of_repositories

        scraper = scraper or Scraper(token=settings.GITHUB_TOKEN)
        try:
            scraper.scrape_individual_users(user_list, **kwargs)
        except RateLimitExceededError as limit_error:
            if self.retry:
                logger.warning(f'--- github rate limit exceeded! '
                               f'retrying automatically in {limit_error.limit_reset_seconds} seconds')

                time.sleep(limit_error.limit_reset_seconds)
                self.handle_individual_users(user_list, scraper=scraper)
                return
            else:
                logger.error('--- github rate limit was exceeded! scraping stopped.')
        logger.info(f'- users added: {scraper.users_added}, repositories added: {scraper.repositories_added}')

    def handle_users_range(self, scraper: Scraper = None):
        kwargs: Dict[str, Any] = {
            'since': self.since,
            'number_of_users': self.number_of_users,
            'number_of_repositories': self.number_of_repositories
        }
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        scraper = scraper or Scraper(token=settings.GITHUB_TOKEN)

        try:
            scraper.scrape_users(**kwargs)
        except RateLimitExceededError as limit_error:
            if self.retry:
                logger.warning(f'--- github rate limit exceeded! '
                               f'continuing automatically in {limit_error.limit_reset_seconds} seconds')
                logger.info(f'--- rate limit reached at id {limit_error.last_id} '
                            f'with {scraper.users_processed} users processed.')

                time.sleep(limit_error.limit_reset_seconds)
                logger.info('--- rate limit reset time elapsed. picking up where we left.')

                self.since = limit_error.last_id
                self.number_of_users = self.number_of_users - scraper.users_processed
                logger.info(f'- scraping remaining {self.number_of_users} users starting at id {self.since}')
                self.handle_users_range(scraper=scraper)
                return
            else:
                logger.error('--- github rate limit was exceeded! scraping stopped.')
        logger.info(f'users added: {scraper.users_added}, repositories added: {scraper.repositories_added}')
