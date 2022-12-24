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
    path('filters', filters, name='filters')
]
