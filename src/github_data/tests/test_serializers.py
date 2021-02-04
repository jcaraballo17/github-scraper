import json
from typing import Dict

from django.test import TestCase
from rest_framework.serializers import ModelSerializer

from github_data.models import GithubUser, GithubRepository
from github_data.serializers import GithubUserSerializer, GithubRepositorySerializer


class TestUserSerializer(TestCase):
    def setUp(self):
        self.user: GithubUser = GithubUser(id=405, login='isthisarealuser', url='https://api.github.com/users/_')
        self.json_git_data: str = '''{
            "login": "test-user",
            "id": 4031,
            "node_id": "*",
            "avatar_url": "https://avatars.githubusercontent.com/u/__?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/_",
            "html_url": "https://github.com/_",
            "type": "User",
            "site_admin": false
        }'''

    def test_correct_user_structure(self):
        dict_representation: Dict = {
            'id': 405,
            'login': 'isthisarealuser',
            'url': 'https://api.github.com/users/_'
        }

        serializer: ModelSerializer = GithubUserSerializer(instance=self.user)
        self.assertEqual(json.dumps(serializer.data), json.dumps(dict_representation))

    def test_github_user_dataset_validation(self):
        serializer: ModelSerializer = GithubUserSerializer(data=json.loads(self.json_git_data))
        serializer.is_valid()
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertTrue(GithubUser.objects.filter(login='test-user').exists())


class TestRepositorySerializer(TestCase):
    def setUp(self):
        self.json_git_data: str = '''{
            "id": 39182718,
            "node_id": "MDEwOlJlcG9zaXRvcnkzOTE4MjcxOA==",
            "name": "secret-webpage",
            "full_name": "another-test-user/secret-webpage",
            "private": false,
            "owner": {
                "login": "another-test-user",
                "id": 4700505,
                "node_id": "MDQ6VXNlcjQ3MDA1MDU=",
                "avatar_url": "https://avatars.githubusercontent.com/u/__?v=4",
                "url": "https://api.github.com/users/_",
                "html_url": "https://github.com/_",
                "type": "User",
                "site_admin": false
            },
            "html_url": "https://github.com/_/_",
            "description": "",
            "fork": false,
            "url": "https://api.github.com/repos/_/_",
            "default_branch": "master"
        }'''

        user: GithubUser = GithubUser(id=400, login='isthisarealuser', url='https://api.github.com/users/_')
        self.repository: GithubRepository = GithubRepository(
            id=888, owner=user, full_name='isthisarealuser/electrify-me', name='electrify-me',
            description='', url='https://api.github.com/repos/_/_'
        )

    def test_correct_repository_structure(self):
        dict_representation: Dict = {
            'id': 888,
            'owner': {
                'id': 400,
                'login': 'isthisarealuser',
                'url': 'https://api.github.com/users/_'
            },
            'full_name': 'isthisarealuser/electrify-me',
            'name': 'electrify-me',
            'description': '',
            'url': 'https://api.github.com/repos/_/_'
        }


        serializer: ModelSerializer = GithubRepositorySerializer(instance=self.repository)
        self.assertEqual(json.dumps(serializer.data), json.dumps(dict_representation))

    def test_github_repository_dataset_validation(self):
        serializer: ModelSerializer = GithubRepositorySerializer(data=json.loads(self.json_git_data))
        serializer.is_valid()
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertTrue(GithubUser.objects.filter(login='another-test-user').exists())
        self.assertTrue(GithubRepository.objects.filter(full_name='another-test-user/secret-webpage').exists())

    def test_github_repository_dataset_validation_existing_user(self):
        GithubUser.objects.create(id=4700505, login='another-test-user', url="https://api.github.com/users/_")

        serializer: ModelSerializer = GithubRepositorySerializer(data=json.loads(self.json_git_data))
        serializer.is_valid()
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertTrue(GithubRepository.objects.filter(full_name='another-test-user/secret-webpage').exists())
