from rest_framework import serializers
from .models import Transaction, Customer
from django.contrib.auth.models import User

class TransactionSerializer(serializers.ModelSerializer):
    product_id_quantity = serializers.SerializerMethodField()
    pin_code = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'customer', 'merchant', 'product_id_quantity', 'total_amount', 'pin_code', 'timestamp']

    def get_product_id_quantity(self, obj):
        return obj.quantity_list()

    def get_pin_code(self,obj):
        return obj.customer.pin_code

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']