from rest_framework import serializers
from .models import Transaction, Customer, TransactionProduct, Product, Filter
from django.contrib.auth.models import User

class TransactionSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    merchant_name = serializers.SerializerMethodField()
    product_quantity = serializers.SerializerMethodField()
    product_id_quantity = serializers.SerializerMethodField()
    pin_code = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'customer', 'customer_name', 'merchant', 'merchant_name', 'product_quantity', 'product_id_quantity', 'total_amount', 'pin_code', 'timestamp']

    def get_customer_name(self, obj):
        return obj.customer.name

    def get_merchant_name(self, obj):
        return obj.merchant.username

    def get_product_quantity(self, obj):
        products = obj.products.all()
        quantites = []
        for product_ in products:
            quantites.append(TransactionProduct.objects.get(transaction = obj, product = product_).quantity)
        products_name = [product.name for product in products]
        return list(zip(products_name,quantites))

    def get_product_id_quantity(self, obj):
        return obj.quantity_list()

    def get_pin_code(self,obj):
        return obj.customer.pin_code

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = '__all__'