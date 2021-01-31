from typing import List

from github_scraper.settings.common import *

SECRET_KEY: str = config.get('secret_key')
if not SECRET_KEY:
    exit('The secret key is required in the settings.json file.')

DEBUG: bool = config.get('debug_mode')

ALLOWED_HOSTS: List[str] = config.get('hostnames', ['localhost'])
