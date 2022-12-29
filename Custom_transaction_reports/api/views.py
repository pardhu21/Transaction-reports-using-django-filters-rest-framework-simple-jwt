from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .filters import TransactioFilter
from .serializer import TransactionSerializer, CustomerSerializer, RegisterSerializer, LoginSerializer, ProductSerializer, FilterSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.

class TransactionList(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransactioFilter
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transacion(request, transaction_id):
    transactions = Transaction.objects.get(pk = transaction_id)
    serializer = TransactionSerializer(transactions)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def merchant_transactions(request, merchant_id):
    merchant = User.objects.get(pk=merchant_id)
    transacions = merchant.transaction_set.all()
    serializer = TransactionSerializer(transacions, many = True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_transactions(request, customer_id):
    customer = Customer.objects.get(pk=customer_id)
    transacions = customer.transaction_set.all()
    serializer = TransactionSerializer(transacions, many = True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customers(request):
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many = True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer(request, customer_id):
    customer = Customer.objects.get(pk = customer_id)
    serializer = CustomerSerializer(customer)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many = True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product(request, product_id):
    product = Product.objects.get(pk = product_id)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['GET', 'PATCH', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def filter(request, username):
    if request.method == 'PATCH':
        filter = Filter.objects.get(pk = request.data['id'])
        serializer = FilterSerializer(filter, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        serializer = FilterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        filter = Filter.objects.get(pk = request.data['id'])
        filter.delete()
        return Response(status=status.HTTP_200_OK)
    user = User.objects.get(username = username)
    filters = user.filter_set.all()
    serializer = FilterSerializer(filters, many = True)
    return Response(serializer.data)

@api_view(['GET'])
def filter_id(request, filter_id):
    filter_id = int(filter_id)
    filter = Filter.objects.get(pk = filter_id)
    serializer = FilterSerializer(filter)
    return Response(serializer.data)


class RegisterAPIView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.data.get('username')
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = User(username = username, email = email)
            user.set_password(password)
            user.save()
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response({'username' : user.username, 
                            'token' : token}, 
                                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response({
                'username' : user.username,
                'token' : token
            })
        return Response(status=status.HTTP_400_BAD_REQUEST)