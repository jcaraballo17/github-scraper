from typing import List

from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from github_data.models import GithubUser, GithubRepository


class RootAPITestCase(APITestCase):
    """
    Tests for the browsable API root view where the endpoints are listed.
    """
    def setUp(self) -> None:
        self.url: str = reverse('api-root')
        self.endpoint_list: List[str] = ['users', 'repos']

    def test_root_response(self) -> None:
        root_response: Response = self.client.get(self.url, format='json')
        self.assertEqual(root_response.status_code, status.HTTP_200_OK)
        self.assertListEqual(list(root_response.data), self.endpoint_list)


class UserAPITestCase(APITestCase):
    """
    Tests for the GithubUser model Viewset.
    """
    @classmethod
    def setUpTestData(cls) -> None:
        GithubUser.objects.create(id=1, login='jcaraballo17', url='https://api.github.com/users/_')
        GithubUser.objects.create(id=2, login='stevencatalino', url='https://api.github.com/users/_')
        GithubUser.objects.create(id=3, login='marioscience', url='https://api.github.com/users/_')

    def test_users_list(self) -> None:
        list_url: str = reverse('user-list')
        response: Response = self.client.get(list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), GithubUser.objects.count())
        self.assertIsInstance(response.data, list)

    def test_filtered_users_list(self) -> None:
        list_url: str = reverse('user-list')
        response: Response = self.client.get(f'{list_url}?since=1', format='json')
        filtered_ids: List[int] = [user.get('id') for user in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), GithubUser.objects.filter(id__in=filtered_ids).count())

    def test_empty_users_list(self) -> None:
        list_url: str = reverse('user-list')
        response: Response = self.client.get(f'{list_url}?since=5', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_user_detail(self) -> None:
        detail_url: str = reverse('user-detail', kwargs={'login': 'jcaraballo17'})
        user: GithubUser = GithubUser.objects.get(login='jcaraballo17')
        response: Response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), user.id)
        self.assertEqual(response.data.get('login'), user.login)

    def test_user_not_found_detail(self) -> None:
        detail_url: str = reverse('user-detail', kwargs={'login': 'no-user-at-all'})
        response: Response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RepositoryAPITestCase(APITestCase):
    """
    Tests for the GithubRepository model Viewset.
    """
    @classmethod
    def setUpTestData(cls) -> None:
        GithubUser.objects.create(id=1, login='jcaraballo17', url='https://api.github.com/users/_')
        GithubUser.objects.create(id=2, login='stevencatalino', url='https://api.github.com/users/_')
        GithubUser.objects.create(id=3, login='marioscience', url='https://api.github.com/users/_')
        GithubRepository.objects.create(
            id=1, owner_id=1, name='prigogine-chaos-quotes',
            full_name='jcaraballo17/complexity-obsession', url='https://api.github.com/repos/_'
        )
        GithubRepository.objects.create(
            id=2, owner_id=1, name='nonlinear-stuff',
            full_name='jcaraballo17/nonlinear-stuff', url='https://api.github.com/repos/_'
        )
        GithubRepository.objects.create(
            id=3, owner_id=2, name='instant-repo',
            full_name='stevencatalino/instant-repo', url='https://api.github.com/repos/_'
        )

    def test_repositories_list(self) -> None:
        list_url: str = reverse('repository-list')
        response: Response = self.client.get(list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), GithubRepository.objects.count())
        self.assertIsInstance(response.data, list)

    def test_user_repositories_list(self) -> None:
        list_url: str = reverse('user-repository-list', kwargs={'login': 'jcaraballo17'})
        response: Response = self.client.get(list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), GithubUser.objects.get(login='jcaraballo17').repositories.count())

    def test_user_repositories_empty_list(self) -> None:
        list_url: str = reverse('user-repository-list', kwargs={'login': 'marioscience'})
        response: Response = self.client.get(list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_user_not_found_repositories(self) -> None:
        list_url: str = reverse('user-repository-list', kwargs={'login': 'phoebebridgers'})
        response: Response = self.client.get(list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_repository_detail(self) -> None:
        detail_url: str = reverse('repository-detail', kwargs={'owner': 'jcaraballo17', 'name': 'nonlinear-stuff'})
        repository: GithubRepository = GithubRepository.objects.get(full_name='jcaraballo17/nonlinear-stuff')
        response: Response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('owner').get('id'), repository.owner_id)
        self.assertEqual(response.data.get('name'), repository.name)

    def test_detail_not_found(self) -> None:
        detail_url: str = reverse('repository-detail', kwargs={'owner': 'who-knows', 'name': 'lomelda'})
        response: Response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
