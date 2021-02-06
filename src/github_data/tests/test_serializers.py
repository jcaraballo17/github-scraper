import json
from typing import Dict

from django.test import TestCase
from rest_framework.serializers import ModelSerializer

from github_data.models import GithubUser, GithubRepository
from github_data.serializers import GithubUserSerializer, GithubRepositorySerializer


class UserSerializerTestCase(TestCase):
    """
    Tests for the DRF GithubUser Model Serializer.
    """
    def test_correct_user_structure(self) -> None:
        user: GithubUser = GithubUser(id=405, login='isthisarealuser', url='https://api.github.com/users/_')
        dict_representation: Dict = {
            'id': 405,
            'login': 'isthisarealuser',
            'url': 'https://api.github.com/users/_'
        }

        serializer: ModelSerializer = GithubUserSerializer(instance=user)
        self.assertJSONEqual(json.dumps(serializer.data), json.dumps(dict_representation))

    def test_github_user_dataset_validation(self) -> None:
        json_git_data: str = '''{
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
        serializer: ModelSerializer = GithubUserSerializer(data=json.loads(json_git_data))
        serializer.is_valid()
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertTrue(GithubUser.objects.filter(login='test-user').exists())


class RepositorySerializerTestCase(TestCase):
    """
    Tests for the DRF GithubRepository Model Serializer.
    """
    def setUp(self) -> None:
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

    def test_correct_repository_structure(self) -> None:
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

        user: GithubUser = GithubUser(id=400, login='isthisarealuser', url='https://api.github.com/users/_')
        repository: GithubRepository = GithubRepository(
            id=888, owner=user, full_name='isthisarealuser/electrify-me', name='electrify-me',
            description='', url='https://api.github.com/repos/_/_'
        )

        serializer: ModelSerializer = GithubRepositorySerializer(instance=repository)
        self.assertJSONEqual(json.dumps(serializer.data), json.dumps(dict_representation))

    def test_github_repository_dataset_validation(self) -> None:
        serializer: ModelSerializer = GithubRepositorySerializer(data=json.loads(self.json_git_data))
        serializer.is_valid()
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertTrue(GithubUser.objects.filter(login='another-test-user').exists())
        self.assertTrue(GithubRepository.objects.filter(full_name='another-test-user/secret-webpage').exists())

    def test_github_repository_dataset_validation_existing_user(self) -> None:
        GithubUser.objects.create(id=4700505, login='another-test-user', url="https://api.github.com/users/_")

        serializer: ModelSerializer = GithubRepositorySerializer(data=json.loads(self.json_git_data))
        serializer.is_valid()
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertTrue(GithubRepository.objects.filter(full_name='another-test-user/secret-webpage').exists())
