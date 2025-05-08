from rest_framework import serializers
from .models import EventList, SantaPair

class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventList
        fields = '__all__'

class SantaPairSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(
        slug_field='eventID',
        queryset=EventList.objects.all()
    )

    class Meta:
        model = SantaPair
        fields = ['id', 'event', 'santaPair']