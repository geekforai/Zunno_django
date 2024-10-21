# serializers.py
from rest_framework import serializers
from .models import BrandCreation

class BrandCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandCreation
        fields = '__all__'  # Include all fields from the model
