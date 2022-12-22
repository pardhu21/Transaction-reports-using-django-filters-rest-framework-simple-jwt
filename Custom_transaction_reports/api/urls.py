from django.urls import path
from .views import *

urlpatterns = [
    path('transaction', TransactionList.as_view(), name='transactions'),
    path('transaction/<int:transaction_id>', transacion, name='transaction'),
    path('transaction/merchant/<int:merchant_id>', merchant_transactions, name='merchant-transactions'),
    path('transaction/customer/<int:customer_id>', customer_transactions, name='customer-transactions'),
    path('customer', customers, name='customers'),
    path('customer/<int:customer_id>',customer, name='customer'),
    path('register', RegisterAPIView.as_view(), name='api-register'),
    path('login', LoginAPIView.as_view(), name='api-login'),
    path('bogus', bogus)
]
