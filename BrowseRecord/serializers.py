from rest_framework import serializers
from .models import BrowseRecord

class BrowseRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrowseRecord
        fields = '__all__'
