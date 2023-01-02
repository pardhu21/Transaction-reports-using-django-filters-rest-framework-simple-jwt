from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import requests,json
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
# Create your views here.
class Tokens:
    BASE_URL = 'http://127.0.0.1:8000'

def home(request):
    return render(request, 'auditor/home.html')

def login_page(request):
    return render(request, 'auditor/login.html')

def register(request):
    return render(request, 'auditor/register.html')

def logout_user(request):
    logout(request)
    response = redirect('home')
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    messages.success(request,'Successfully logged out')
    return response

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
            response = redirect('dashboard')
            response.set_cookie('access', data['token']['access'])
            response.set_cookie('refresh', data['token']['refresh'])
            login(request, user)
            messages.success(request, 'Successfully logged in')
            return response
        if data.status_code == 400:
            messages.warning(request, 'Invalid credentials, please enter correct details')
            return redirect('login')
        
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('re-password')
        if User.objects.filter(username = username).count() != 0:
            messages.warning(request, 'This username is already used')
            return redirect('register')
        if password != re_password:
            messages.warning(request, 'Passwords do not match')
            return redirect('register')
        if len(password) < 8:
            messages.warning(request, 'password is not long enough')
            return redirect('register')
        url = reverse('api:register')
        details = {
            "username": username,
            "email": email,
            "password": password
        }
        data = requests.post(url = Tokens.BASE_URL + url, data = details)
        if data.status_code == 201:
            data = data.json()
            user = User.objects.get(username = username)
            response = redirect('dashboard')
            response.set_cookie('access', data['token']['access'])
            response.set_cookie('refresh', data['token']['refresh'])
            login(request, user)
            messages.success(request, 'Account created successfully')
            return response
        if data.status_code == 400:
            messages.warning(request, 'Invalid credentials, please enter correct details')
            return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    url = reverse('api:transactions')
    data = send_request(request, url)
    return render(request, 'auditor/dashboard-dashboard.html', {'data' : data[:-11:-1]})

@login_required(login_url='login')
def transactions(request):
    url = reverse('api:transactions')
    data = send_request(request, url)
    paginator = Paginator(data, 15)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    return render(request, 'auditor/transactions-dashboard.html', {'transactions' : transactions})

@login_required(login_url='login')
def products(request):
    url = reverse('api:products')
    data = send_request(request, url)
    return render(request, 'auditor/products-dashboard.html', {'products' : data})

@login_required(login_url='login')
def customers(request):
    url = reverse('api:customers')
    data = send_request(request, url)
    return render(request, 'auditor/customers-dashboard.html', {'customers' : data})

@login_required(login_url='login')
def filters(request):
    if request.method == 'POST':
        url = Tokens.BASE_URL + reverse('api:filter', kwargs={'username' : request.user})
        if request.POST.get('delete'):
            requests.delete(url=url, json={"id":int(request.POST['delete'])}, headers={'authorization':'Bearer ' + request.COOKIES['access'], 'content-type': 'application/json'})
            messages.info(request, 'Filter deleted successfully')
        else:
            post = {}
            for i in request.POST:
                if request.POST[i] != 'None':
                    post[i] = request.POST[i]
            feilds = {'submit-btn':'id', 'name':'name', 'amount-lt':'total_amount_lower_than', 'amount-gt':'total_amount_greater_than', 'customer-name':'customer_name', 'pin-code':'pin_code'}
            body ={}
            for i in feilds:
                if post.get(i):
                    body[feilds[i]] = post.get(i)
            for i in body:
                if i in ['id', 'total_amount_lower_than', 'total_amount_greater_than', 'pin_code']:
                    body[i] = int(body[i])
            body['user'] = request.user.id
            result = json.dumps(body)
            result = json.loads(result)
            if not body.get('id'):
                response = requests.post(url=url, json=body, headers={'authorization':'Bearer ' + request.COOKIES['access'], 'content-type': 'application/json'})
            else:
                response = requests.patch(url=url, json=body, headers={'authorization':'Bearer ' + request.COOKIES['access'], 'content-type': 'application/json'})
            if response.status_code == 201:
                messages.success(request, 'Filter created successfully')
            elif response.status_code != 200:
                messages.error(request, 'Something wrong has happened')
            else:
                messages.info(request, 'Successfully modifed the filter')
    
    url = reverse('api:filter', kwargs={'username': request.user})
    data = send_request(request, url)
    return render(request, 'auditor/filters-dashboard.html', {'filters' : data})

@login_required(login_url='login')
def product_volume(request):
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, url)
    return render(request, 'auditor/product-volume.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

@login_required(login_url='login')
def product_value(request):
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, url)
    return render(request, 'auditor/product-value.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

@login_required(login_url='login')
def customer_volume(request):
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, url)
    return render(request, 'auditor/customer-volume.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

@login_required(login_url='login')
def customer_value(request):
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, url)
    return render(request, 'auditor/customer-value.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

@login_required(login_url='login')
def complete_report(request):
    filter_url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, filter_url)
    return render(request, 'auditor/complete-report.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})


@login_required(login_url='login')
def get_product_volume(request, query):
    transactions_url = reverse('api:transactions')
    if query == 'x':
        transactions = send_request(request, transactions_url)
    else:
        transactions = send_request(request, transactions_url + '?' + query)
    product_volume = {}
    for transaction in transactions:
        for i in transaction['product_quantity']:
            if product_volume.get(i[0]):
                product_volume[i[0]] += i[1]
            else:
                product_volume[i[0]] = i[1]
    product_volume = {k:v for k, v in sorted(product_volume.items(), key=lambda x : x[1], reverse=True)}
    return JsonResponse(product_volume, safe=False)

@login_required(login_url='login')
def get_product_value(request,query):
    transactions_url = reverse('api:transactions')
    if query == 'x':
        transactions = send_request(request, transactions_url)
    else:
        transactions = send_request(request, transactions_url + '?' + query)
    product_volume = {}
    for transaction in transactions:
        for i in transaction['product_quantity']:
            if product_volume.get(i[0]):
                product_volume[i[0]] += i[1]
            else:
                product_volume[i[0]] = i[1]
    products_url = reverse('api:products')
    products = send_request(request, products_url)
    product_value = {}
    for i in product_volume:
        for product in products:
            if i == product['name']:
                product_value[i] = product['cost'] * product_volume[i]
    product_value = {k:v for k, v in sorted(product_value.items(), key=lambda x : x[1], reverse=True)}
    return JsonResponse(product_value, safe=False)

@login_required(login_url='login')
def get_customer_volume(request, query):
    transactions_url = reverse('api:transactions')
    if query == 'x':
        transactions = send_request(request, transactions_url)
    else:
        transactions = send_request(request, transactions_url + '?' + query)
    customer_volume = {}
    for transaction in transactions:
        if customer_volume.get(transaction['customer']):
            customer_volume[transaction['customer']] += len(transaction['product_quantity'])
        else:
            customer_volume[transaction['customer']] = len(transaction['product_quantity'])
    customer_volume = get_customer_dict(request, customer_volume)
    return JsonResponse(customer_volume, safe=False)

@login_required(login_url='login')
def get_customer_value(request,query):
    transactions_url = reverse('api:transactions')
    if query == 'x':
        transactions = send_request(request, transactions_url)
    else:
        transactions = send_request(request, transactions_url + '?' + query)
    customer_value = {}
    for transaction in transactions:
        if customer_value.get(transaction['customer']):
            customer_value[transaction['customer']] += transaction['total_amount']
        else:
            customer_value[transaction['customer']] = transaction['total_amount']
    customer_value = get_customer_dict(request, customer_value)
    return JsonResponse(customer_value, safe=False)

@login_required(login_url='login')
def get_transactions(request, query = None):
    url = reverse('api:transactions')
    if query:
        transactions = send_request(request, url + '?' + query)
    else:
        transactions = send_request(request, url)
    return JsonResponse(transactions, safe=False)

def get_customer_dict(request, customer_dict):
    customers = send_request(request, reverse('api:customers'))
    new_dict = {}
    for i in customer_dict:
        for j in customers:
            if i == j['id']:
                new_dict[j['name']] = customer_dict[i]
    new_dict = {k:v for k, v in sorted(new_dict.items(), key=lambda x : x[1], reverse=True)}
    return new_dict

def send_request(request, url, params = None):
    if params:
        data = requests.get(url = Tokens.BASE_URL + url, params=params, headers={'authorization':'Bearer ' + request.COOKIES['access'], 'content-type': 'application/json'})
    else:
        data = requests.get(url = Tokens.BASE_URL + url, headers={'authorization':'Bearer ' + request.COOKIES['access'], 'content-type': 'application/json'})
    if data.status_code == 200:
        return data.json()
    if data.status_code == 401:
        url_ = Tokens.BASE_URL + reverse('token_refresh')
        data_ = requests.post(url = url_, data = {"refresh": request.COOKIES['refresh']})
        if data_.status_code == 400:
            return redirect('login')
        request.COOKIES['access'] = data_.json()['access']
        return send_request(request, url)
                                        