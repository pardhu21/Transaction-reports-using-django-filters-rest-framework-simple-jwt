from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .filters import TransactioFilter
from .serializer import TransactionSerializer, CustomerSerializer
from django.contrib.auth.models import User
# Create your views here.

class TransactionList(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransactioFilter

@api_view(['GET'])
def transacion(request, transaction_id):
    transactions = Transaction.objects.get(pk = transaction_id)
    serializer = TransactionSerializer(transactions)
    return Response(serializer.data)

@api_view(['GET'])
def merchant_transactions(request, merchant_id):
    merchant = User.objects.get(pk=merchant_id)
    transacions = merchant.transaction_set.all()
    serializer = TransactionSerializer(transacions, many = True)
    return Response(serializer.data)

@api_view(['GET'])
def customer_transactions(request, customer_id):
    customer = Customer.objects.get(pk=customer_id)
    transacions = customer.transaction_set.all()
    serializer = TransactionSerializer(transacions, many = True)
    return Response(serializer.data)

@api_view(['GET'])
def customers(request):
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers)
    return Response(serializer.data)

@api_view(['GET'])
def customer(request, customer_id):
    customer = Customer.objects.get(pk = customer_id)
    serializer = CustomerSerializer(customer)
    return Response(serializer.data)