from github_scraper.settings.common import *

SECRET_KEY: str = 'thisisanotsosecretkeyfortravis'
DEBUG: bool = False
DATABASES = {
    'default': {
        'name': 'travis_ci_db',
        'engine': 'django.db.backends.postgresql',
        'user': 'travis',
        'password': '',
        'host': 'localhost',
    }
}
