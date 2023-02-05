from rest_framework import serializers

class FitlerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    total_amount_lower_than = serializers.IntegerField()
    total_amount_greater_than = serializers.IntegerField()
    customer_name = serializers.CharField()
    pin_code = serializers.IntegerField()
    user = serializers.ImageField()