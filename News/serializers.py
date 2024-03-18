from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = News
        fields = '__all__'
