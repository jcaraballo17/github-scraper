from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from github_data.views import api_root, user_list, user_detail, \
    repository_list, repository_detail, user_repository_list

urlpatterns = format_suffix_patterns([
    path('', api_root, name='api-root'),

    path('users/', user_list, name='user-list'),
    path('users/<str:login>/', user_detail, name='user-detail'),
    path('users/<str:login>/repos/', user_repository_list, name='user-repository-list'),

    path('repos/', repository_list, name='repository-list'),
    path('repos/<str:owner>/<str:name>/', repository_detail, name='repository-detail'),
])
