from github_scraper.settings.common import *

SECRET_KEY: str = 'thisisanotsosecretkeyfortravis'
DEBUG: bool = False
DATABASES = {
    'default': {
        'NAME': 'travis_ci_db',
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': 'localhost',
    }
}
