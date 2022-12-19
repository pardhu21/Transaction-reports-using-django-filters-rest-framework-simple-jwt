from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializer import TransactionSerializer
from django.contrib.auth.models import User
# Create your views here.

@api_view(['GET'])
def transacions(request):
    transactions = Transaction.objects.all()
    serializer = TransactionSerializer(transactions, many = True)
    return Response(serializer.data)

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