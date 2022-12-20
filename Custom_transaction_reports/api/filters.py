import django_filters
from .models import Transaction, Customer

class TransactioFilter(django_filters.FilterSet):
    class Meta:
        model = Transaction
        fields = {
            'total_amount': ['lt', 'gt'],
            'customer__name' : ['icontains'],
            'timestamp' : ['lt', 'gt']
        }