from rest_framework import serializers
from .models import DataOperationModel

class DataOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataOperationModel
        fields = '__all__'
