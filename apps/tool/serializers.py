from rest_framework_mongoengine import serializers
from apps.tool.models import Predict, Model

class PredictSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Predict
        fields = '__all__'

class ModelSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Model
        fields = '__all__'