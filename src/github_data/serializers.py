from rest_framework import serializers

from github_data.models import GithubUser, GithubRepository


class GithubUserSerializer(serializers.ModelSerializer):
    """
    Rest Framework ModelSerializer for the GithubUser model.
    """
    class Meta:
        model = GithubUser
        fields = ['id', 'login', 'url']


class GithubRepositorySerializer(serializers.ModelSerializer):
    """
    Rest Framework ModelSerializer for the GithubRepository model.
    """
    owner = GithubUserSerializer(read_only=True)

    class Meta:
        model = GithubRepository
        fields = ['id', 'owner', 'full_name', 'name', 'description', 'url']

    def create(self, validated_data):
        """
        Method override to make sure there Repository owner was already inserted into the database,
        and to make sure the ForeignKey owner_id attribute is in the Repository dataset.
        :param validated_data: Already validated Repository data to insert to the database.
        :return: The newly created GithubRepository object
        """
        owner_data = self.initial_data.get('owner')
        if not GithubUser.objects.filter(id=owner_data.get('id')).exists():
            user_serializer = GithubUserSerializer(data=owner_data)
            if user_serializer.is_valid():
                user_serializer.save()

        repository = GithubRepository.objects.create(**validated_data, owner_id=owner_data.get('id'))
        return repository
