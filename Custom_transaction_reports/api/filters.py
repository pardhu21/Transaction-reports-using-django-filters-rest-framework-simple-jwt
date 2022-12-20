import django_filters
from .models import Transaction

class TransactioFilter(django_filters.FilterSet):
    class Meta:
        model = Transaction
        fields = ['id', 'total_amount']