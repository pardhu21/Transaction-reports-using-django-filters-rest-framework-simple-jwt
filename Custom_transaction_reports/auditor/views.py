from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
import requests
from django.http import HttpResponse

# Create your views here.
class Tokens:
    TOKEN = ''
    REFRESH = ''
    BASE_URL = 'http://127.0.0.1:8000'

def home(request):
    return render(request, 'auditor/home.html')

def login_page(request):
    return render(request, 'auditor/login.html')

def register(request):
    return render(request, 'auditor/register.html')

def logout_user(request):
    logout(request)
    return redirect('home')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        url = reverse('api:login')
        details = {
            "username": username,
            "password": password
        }
        data = requests.post(url = Tokens.BASE_URL + url, data=details)
        if data.status_code == 200:
            data = data.json()
            user = User.objects.get(username = username)
            Tokens.TOKEN = data['token']['access']
            Tokens.REFRESH = data['token']['refresh']
            login(request, user)
            return redirect('dashboard')
        
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        url = reverse('api:register')
        details = {
            "username": username,
            "email": email,
            "password": password
        }
        data = requests.post(url = url, data = details)
        if data.status_code == 201:
            data = data.json()
            user = User.objects.get(username = username)
            Tokens.TOKEN = data['token']['access']
            Tokens.REFRESH = data['token']['refresh']
            login(request, user)
            return redirect('dashboard')

def dashboard(request):
    url = reverse('api:transactions')
    data = send_request(url)
    return render(request, 'auditor/dashboard-dashboard.html', {'data' : data[:-11:-1]})

def transactions(request):
    url = reverse('api:transactions')
    data = send_request(url)
    return render(request, 'auditor/transactions-dashboard.html', {'transactions' : data})

def products(request):
    url = reverse('api:products')
    data = send_request(url)
    return render(request, 'auditor/products-dashboard.html', {'products' : data})

def customers(request):
    url = reverse('api:customers')
    data = send_request(url)
    return render(request, 'auditor/customers-dashboard.html', {'customers' : data})

def filters(request):
    url = reverse('api:filter', kwargs={'username': request.user})
    data = send_request(url)
    return render(request, 'auditor/filters-dashboard.html', {'filters' : data})

def product_volume(request):
    product_volume = get_product_volume()
    return HttpResponse(product_volume.items())

def product_value(request):
    product_value = get_product_value()
    return HttpResponse(product_value.items())

def customer_volume(request):
    pass

def customer_value(request):
    pass

def complete_report(request):
    pass

def get_product_volume():
    transactions_url = reverse('api:transactions')
    transactions = send_request(transactions_url)
    product_volume = {}
    for transaction in transactions:
        for i in transaction['product_quantity']:
            if product_volume.get(i[0]):
                product_volume[i[0]] += i[1]
            else:
                product_volume[i[0]] = i[1]
    return product_volume

def get_product_value():
    product_volume = get_product_volume()
    products_url = reverse('api:products')
    products = send_request(products_url)
    product_value = {}
    for i in product_volume:
        for product in products:
            if i == product['name']:
                product_value[i] = product['cost'] * product_volume[i]
    return product_value

def send_request(url):
    url = Tokens.BASE_URL + url
    data = requests.get(url = url, headers={'authorization':f'Bearer {Tokens.TOKEN}', 'content-type': 'application/json'})
    if data.status_code == 200:
        return data.json()
    if data.status_code == 401:
        url_ = Tokens.BASE_URL + reverse('token_refresh')
        data_ = requests.post(url = url_, data = {"refresh": Tokens.REFRESH})
        if data_.status_code == 400:
            return redirect('login')
        Tokens.TOKEN = data_.json()['access']
        return send_request(url)

# def get_new_token(request):
#     url = 'http://127.0.0.1:8000/api/token/refresh/'
#     data = requests.post(url = url, data = {"refresh": Tokens.refresh})
#     Tokens.token = data.json()['access']
                                        