from typing import Callable, Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer

from github_data.models import GithubUser, GithubRepository
from github_data.serializers import GithubUserSerializer, GithubRepositorySerializer

function_view = Callable[[Request, Any], Response]


class GithubUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Github Users scraped from the GitHub API.
    """
    queryset: QuerySet = GithubUser.objects.all()
    serializer_class: ModelSerializer = GithubUserSerializer
    lookup_field: str = 'login'

    def list(self, request, *args, **kwargs) -> Response:
        """
        List a queryset and filter it by id if the `since` parameter is present.
        :param request: Request object with all the request data.
        :param args: arguments
        :param kwargs: keyword arguments
        :return: A response with a serialized queryset of Github Users.
        """
        since = request.query_params.get('since')

        if since:
            self.queryset = self.get_queryset().filter(pk__gt=since)
        return super().list(request, *args, **kwargs)


class GithubRepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Github Repositories scraped from the GitHub API.
    """
    queryset: QuerySet = GithubRepository.objects.all()
    serializer_class: ModelSerializer = GithubRepositorySerializer

    @action(detail=False)
    def user_repositories(self, request, *args, **kwargs):
        """
        Custom action to list a User's repositories.
        :param request: Request object with all the request data.
        :param args: arguments
        :param kwargs: keyword arguments
        :return: A response with a serialized queryset of a User's Github Repositories. 404 if the user is not found.
        """
        owner_username: str = kwargs.get('login')
        user: GithubUser = get_object_or_404(GithubUser.objects.all(), login=owner_username)
        queryset: QuerySet = user.repositories.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_object(self) -> GithubRepository:
        """
        Method override that uses a custom lookup to retrieve the object to be displayed in the detail view.
        :return: A GithubRepository instance with the owner username and repository name provided.
        """
        owner: str = self.kwargs.get("owner")
        name: str = self.kwargs.get("name")
        return get_object_or_404(self.get_queryset(), full_name=f'{owner}/{name}')


@api_view(['GET'])
def api_root(request, format: str =None) -> Response:
    """
    Github Scraped data API
    """
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'repos': reverse('repository-list', request=request, format=format)
    })


user_list: function_view = GithubUserViewSet.as_view({'get': 'list'})
user_detail: function_view = GithubUserViewSet.as_view({'get': 'retrieve'})
repository_list: function_view = GithubRepositoryViewSet.as_view({'get': 'list'})
user_repository_list: function_view = GithubRepositoryViewSet.as_view({'get': 'user_repositories'})
repository_detail: function_view = GithubRepositoryViewSet.as_view({'get': 'retrieve'})
