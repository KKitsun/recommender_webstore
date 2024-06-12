from rest_framework import serializers
from .models import Game

class GameCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'price', 'image']