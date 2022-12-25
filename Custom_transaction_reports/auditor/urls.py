from django.urls import path
from .views import *

urlpatterns = [
    path('home', home, name='home'),
    path('login', login_page, name='login'),
    path('register', register, name='register'),
    path('login-user', login_user, name='login-user'),
    path('register-user', register_user, name='register-user'),
    path('logout', logout_user, name='logout'),
    path('dashboard', dashboard, name='dashboard'),
    path('transactions', transactions, name='transactions'),
    path('products', products, name='products'),
    path('customers', customers, name='customers'),
    path('filters', filters, name='filters'),
    path('product-volume', product_volume, name='product-volume'),
    path('product-value', product_value, name='product-value'),
    path('customer-volume', customer_volume, name='customer-volume'),
    path('customer-value', customer_value, name='customer-value'),
    path('complete-report', complete_report, name='complete-report')
]
