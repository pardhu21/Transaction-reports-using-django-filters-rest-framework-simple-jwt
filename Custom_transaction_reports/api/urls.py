from django.urls import path
from .views import *

urlpatterns = [
    path('transaction', transacions, name='transactions'),
    path('transaction/<int:transaction_id>', transacion, name='transaction'),
    path('transaction/merchant/<int:merchant_id>', merchant_transactions, name='merchant-transactions'),
    path('transaction/customer/<int:customer_id>', customer_transactions, name='customer-transactions')
]
