from lawyer_user.User import User
from rest_framework import serializers



class BlogSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'groups']
