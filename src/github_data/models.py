from django.db import models


class GithubUser(models.Model):
    """
    Model representing a GitHub User.
    """
    id = models.IntegerField(primary_key=True, verbose_name='github user id', db_column='github_id')
    login = models.CharField(max_length=39, verbose_name='github login username', unique=True, db_column='github_login')
    url = models.URLField()
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    created_at = models.DateTimeField(editable=False)

    class Meta:
        db_table = 'github_user'
        verbose_name = 'github user'


class GithubRepository(models.Model):
    """
    Model representing a GitHub Repository.
    """
    id = models.IntegerField(primary_key=True, verbose_name='github repository id', db_column='github_id')
    owner = models.ForeignKey(GithubUser, on_delete=models.CASCADE, related_name='repos', null=True)
    full_name = models.CharField(max_length=140, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField()
    created_at = models.DateTimeField(editable=False)

    class Meta:
        db_table = 'github_repository'
        verbose_name = 'github repository'
