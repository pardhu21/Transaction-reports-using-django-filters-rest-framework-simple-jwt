from django.urls import path
from .views import *

app_name = 'api'

urlpatterns = [
    path('transaction', TransactionList.as_view(), name='transactions'),
    path('transaction/<int:transaction_id>', transacion, name='transaction'),
    path('transaction/merchant/<int:merchant_id>', merchant_transactions, name='merchant-transactions'),
    path('transaction/customer/<int:customer_id>', customer_transactions, name='customer-transactions'),
    path('customer', customers, name='customers'),
    path('customer/<int:customer_id>',customer, name='customer'),
    path('product', products, name='products'),
    path('product/<int:product_id>',product, name='product'),
    path('filter/<str:username>', filter, name='filter'),
    path('register', RegisterAPIView.as_view(), name='register'),
    path('login', LoginAPIView.as_view(), name='login'),
]
