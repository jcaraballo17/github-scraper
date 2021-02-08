# github-scraper
> GitHub User and Repository data scraper for take-home assignment.

[![Build Status](https://travis-ci.com/jcaraballo17/github-scraper.svg?branch=main)](https://travis-ci.com/jcaraballo17/github-scraper) 
[![Coverage Status](https://coveralls.io/repos/github/jcaraballo17/github-scraper/badge.svg?branch=main)](https://coveralls.io/github/jcaraballo17/github-scraper?branch=main)

github-scraper is a service written in Python that scrapes User and Repository data from the GitHub API and stores a small subset of the dataset. Additionally, it provides an API to query the scraped data.

## Table of contents
* [Installation and Setup](#installation-and-setup)
* [Usage](#usage)
* [Testing](#testing)
* [Structure and Design](#structure-and-design)

## Installation and Setup
### Requirements
This project uses [Python](https://www.python.org/downloads/) 3.6+ with the following libraries
* [Django](https://www.djangoproject.com/start/overview/) 3.1
* [Django REST Framework](https://www.django-rest-framework.org/)
* [ghapi GitHub Library](https://ghapi.fast.ai/)

### Setup
It is highly encouraged to use a [virtual environment](https://docs.python.org/3/library/venv.html) to create an isolated environment for the project.
##### Create the virtual environment and activate it 
```
python3 -m venv scraper-environment
source ./scraper-environment/bin/activate
```
##### Download source from GitHub
```
git clone https://github.com/jcaraballo17/github-scraper.git
cd github-scraper
```
##### Install requirements
```
pip install -r requirements.txt
```

##### Nagivate to the source directory
The base directory for the Django project is `src`, where the `manage.py` script is.
```
cd src
```

##### Create the project configuration file
The project configuration is stored in a file called `config.json` inside the `github_scraper/settings` directory. You can find a [template of this file](https://github.com/jcaraballo17/github-scraper/blob/main/src/github_scraper/settings/config_template.json) inside the same directory.

Here is an example of `config.json` for a development setting using a sqlite3 database:
```
{
  "secret_key": "UaJYaHUsViHcds5Un3vhEsH-5ZAsXg3V6cgxhToR6wU",
  "github_oauth_token": "b6706204bf1911b29c7208adb5b0ecbrc1f6bad7",
  "debug_mode": true,
  "databases": [
    {
      "connection_name": "default",
      "database_name": "scraper_data.sqlite3",
      "engine": "django.db.backends.sqlite3"
    }
  ]
}
```

Other database managers can also be used, and all the appropriate configuration can be found in the [django official documentation](https://docs.djangoproject.com/en/3.1/ref/settings/#databases).

##### Create the database schema
To create the database schema and tables, run the `migrate` django command
```
python manage.py migrate
```

## Usage
The service has two main parts: 
* The API exposing the scraped data.
* The `scrape_git` django command to scrape data.

Here we'll cover how to use both of them

#### Running the API on Django's development server
After [creating the configuration file](#create-the-project-configuration-file), you should be able to run Django's integrated development server and open it in a Web Browser to use the API.

```
python manage.py runserver
```

##### Running the API on an external server
Configuring a web server is out of the scope of this project, but I recommend following [this guide](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04) on how to set up a project using `nginx` and `gunicorn` to serve a django project in Ubuntu.

After starting the server, you can navigate to http://127.0.0.1:8000 on a web browser and see the available API endpoints.

#### Using the `scrape_git` command

The scrape_git command can be used to get individual users or a range of users starting at an id.

```
Usage:
scrape_git
scrape_git [user] [user] [user]
scrape_git [--since [ID]]
scrape_git [--users [number_of_users]]
scrape_git [--repositories [number_of_repositories]]
scrape_git [--retry]
scrape_git --help
```

##### Examples
Scrape all users and all their repositories (will fail when rate limit is exceeded)
```
python manage.py scrape_git
```

Scrape the users `jcaraballo17` and `Maurier` and all of their repositories
```
python manage.py scrape_git jcaraballo17 Maurier
```

Scrape the user `jcaraballo17` with only one repository
```
python manage.py scrape_git jcaraballo17
```

Scrape the 100 first users with all of their repositories and wait until the rate limit reset time has passed to continue scraping if the rate limit is exceeded
```
python manage.py scrape_git --users 100 --retry
```

Scrape 50 users starting at ID `3000` and 5 repositories for each user
```
python manage.py scrape_git --since 3000 --users 50 --repositories 5
```

## Testing
To test the code with code coverage run
```
pytest --cov=github_data/ --cov-report html
open htmlcov/index.html
```

## Structure and Design

### Python
The project was developed in Python for it's simplicity and versatility. Version 3.6+ of Python was chosed most of all for it's support for type hints.

### Django
Django was used as the web framework for it's powerful ORM, it's Model-View-Template architecture, and the scalability it provides. On the other hand, Django usually ends up being too complicated for small projects, so it was not the first option when considering which web framework to use. The other option considering the scope of the project was [FastAPI](https://fastapi.tiangolo.com/) for it's high performance and simplicity and it's API oriented design.

##### Scope of the scraped data
The github API has extensive User and Repository data. For this project I chose to scrape what I considered to be the most important data for each to keep it simple and easier to develop.

##### Settings file VS environment variables
This was a personal choice and what I'm most used to using for Django projects because all of the configuration is defined in json format in one place.

##### Using a src directory for the project code
Old habits from other programming languages and a code convention in previous jobs.

### ghapi for GitHub API
The ghapi library provides simple and easy to use idiomatic access to the entire GitHub API. The interface is built with GitHub's OpenAPI specification for their REST API, and it's much more simple to use and efficient than other GitHub libraries like [PyGithub](https://github.com/PyGithub/PyGithub).

One setback that I encountered was that because it's a fairly new library, the only reference is the official documentation, which is hard to navigate. This led me to take some not-so-efficient design decisions like the pagination methods in the Scraper tool which are completely unnecessary and complicated the development of the Scraper.
