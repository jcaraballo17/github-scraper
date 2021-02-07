import secrets

from github_scraper.settings.common import *

SECRET_KEY: str = config.get('secret_key', secrets.token_urlsafe())

DEBUG: bool = config.get('debug_mode', True)
