from github_scraper.settings.common import *

SECRET_KEY: str = 'thisisanotsosecretkeyfortravis'
GITHUB_TOKEN: str = os.environ['GITHUB_TOKEN']
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
