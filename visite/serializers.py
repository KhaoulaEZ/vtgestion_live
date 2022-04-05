from rest_framework import routers, serializers, viewsets
from .models import Visite

# Serializers define the API representation.
class VisiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Visite
        fields = '__al__'