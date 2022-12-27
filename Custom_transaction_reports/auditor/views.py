from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
import requests
from django.http import JsonResponse
from django.core.paginator import Paginator
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
    paginator = Paginator(data, 15)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    return render(request, 'auditor/transactions-dashboard.html', {'transactions' : transactions})

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
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(url)
    return render(request, 'auditor/product-volume.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

def product_value(request):
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(url)
    return render(request, 'auditor/product-value.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

def customer_volume(request):
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(url)
    return render(request, 'auditor/customer-volume.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

def customer_value(request):
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(url)
    return render(request, 'auditor/customer-value.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

def complete_report(request):
    filter_url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(filter_url)
    return render(request, 'auditor/complete-report.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})


def get_product_volume(request, query):
    transactions_url = reverse('api:transactions')
    if query == 'x':
        transactions = send_request(transactions_url)
    else:
        transactions = send_request(transactions_url + '?' + query)
    product_volume = {}
    for transaction in transactions:
        for i in transaction['product_quantity']:
            if product_volume.get(i[0]):
                product_volume[i[0]] += i[1]
            else:
                product_volume[i[0]] = i[1]
    product_volume = {k:v for k, v in sorted(product_volume.items(), key=lambda x : x[1], reverse=True)}
    return JsonResponse(product_volume, safe=False)

def get_product_value(request,query):
    transactions_url = reverse('api:transactions')
    if query == 'x':
        transactions = send_request(transactions_url)
    else:
        transactions = send_request(transactions_url + '?' + query)
    product_volume = {}
    for transaction in transactions:
        for i in transaction['product_quantity']:
            if product_volume.get(i[0]):
                product_volume[i[0]] += i[1]
            else:
                product_volume[i[0]] = i[1]
    products_url = reverse('api:products')
    products = send_request(products_url)
    product_value = {}
    for i in product_volume:
        for product in products:
            if i == product['name']:
                product_value[i] = product['cost'] * product_volume[i]
    product_value = {k:v for k, v in sorted(product_value.items(), key=lambda x : x[1], reverse=True)}
    return JsonResponse(product_value, safe=False)

def get_customer_volume(request, query):
    transactions_url = reverse('api:transactions')
    if query == 'x':
        transactions = send_request(transactions_url)
    else:
        transactions = send_request(transactions_url + '?' + query)
    customer_volume = {}
    for transaction in transactions:
        if customer_volume.get(transaction['customer']):
            customer_volume[transaction['customer']] += len(transaction['product_quantity'])
        else:
            customer_volume[transaction['customer']] = len(transaction['product_quantity'])
    customer_volume = get_customer_dict(customer_volume)
    return JsonResponse(customer_volume, safe=False)

def get_customer_value(request,query):
    transactions_url = reverse('api:transactions')
    if query == 'x':
        transactions = send_request(transactions_url)
    else:
        transactions = send_request(transactions_url + '?' + query)
    customer_value = {}
    for transaction in transactions:
        if customer_value.get(transaction['customer']):
            customer_value[transaction['customer']] += transaction['total_amount']
        else:
            customer_value[transaction['customer']] = transaction['total_amount']
    customer_value = get_customer_dict(customer_value)
    return JsonResponse(customer_value, safe=False)

def get_transactions(request, query = None):
    url = reverse('api:transactions')
    if query:
        transactions = send_request(url + '?' + query)
    else:
        transactions = send_request(url)
    return JsonResponse(transactions, safe=False)

def get_customer_dict(customer_dict):
    customers = send_request(reverse('api:customers'))
    new_dict = {}
    for i in customer_dict:
        for j in customers:
            if i == j['id']:
                new_dict[j['name']] = customer_dict[i]
    new_dict = {k:v for k, v in sorted(new_dict.items(), key=lambda x : x[1], reverse=True)}
    return new_dict

def send_request(url, params = None):
    if params:
        data = requests.get(url = Tokens.BASE_URL + url, params=params, headers={'authorization':f'Bearer {Tokens.TOKEN}', 'content-type': 'application/json'})
    else:
        data = requests.get(url = Tokens.BASE_URL + url, headers={'authorization':f'Bearer {Tokens.TOKEN}', 'content-type': 'application/json'})
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
                                        