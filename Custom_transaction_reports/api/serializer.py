from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    total_amount = serializers.SerializerMethodField()
    product_id_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'customer', 'merchant', 'product_id_quantity', 'total_amount', 'timestamp']

    def get_total_amount(self, obj):
        return obj.total_amount()

    def get_product_id_quantity(self, obj):
        return obj.quantity_list()