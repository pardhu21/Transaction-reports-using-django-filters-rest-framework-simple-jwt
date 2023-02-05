from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import requests,json
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages

class Tokens:
    # Change url here if you are running server on host other than 8000
    BASE_URL = 'http://127.0.0.1:8000'

def home(request):
    return render(request, 'auditor/home.html')

def login_page(request):
    return render(request, 'auditor/login.html')

def register(request):
    return render(request, 'auditor/register.html')

def logout_user(request):
    """
    On logout the access token and refresh tokens saved in 
    will be deleted.
    """
    logout(request)
    response = redirect('home')
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    messages.success(request,'Successfully logged out')
    return response

def login_user(request):
    """
    This function will hadle login and on successful login
    details will be sent to api and the returned refresh token
    and access token will be saved in cookies.
    """
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
    """
    Similar to login_user function, this function will handle
    register and set access token and refresh token in cookies.
    """
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
    #This page will display recent ten transaction in a bar graph and table
    url = reverse('api:transactions')
    data = send_request(request, url)
    return render(request, 'auditor/dashboard-dashboard.html', {'data' : data[:-11:-1]})

@login_required(login_url='login')
def transactions(request):
    # This page will show all tranactions
    url = reverse('api:transactions')
    data = send_request(request, url)
    paginator = Paginator(data, 15)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)
    return render(request, 'auditor/transactions-dashboard.html', {'transactions' : transactions})

@login_required(login_url='login')
def products(request):
    # This page will show all products
    url = reverse('api:products')
    data = send_request(request, url)
    return render(request, 'auditor/products-dashboard.html', {'products' : data})

@login_required(login_url='login')
def customers(request):
    # This page will show all customers in a table
    url = reverse('api:customers')
    data = send_request(request, url)
    return render(request, 'auditor/customers-dashboard.html', {'customers' : data})

@login_required(login_url='login')
def filters(request):
    """
    HTML contains multiple forms and on posting the data
    and the data will be to sent to api app and it will be 
    modified or deleted or created depending on the requirement
    """
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
    # Shows a pie chart containing product volume 
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, url)
    return render(request, 'auditor/product-volume.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

@login_required(login_url='login')
def product_value(request):
    # Shows a pie chart containing product value
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, url)
    return render(request, 'auditor/product-value.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

@login_required(login_url='login')
def customer_volume(request):
    # Shows a pie chart containing customer volume
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, url)
    return render(request, 'auditor/customer-volume.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

@login_required(login_url='login')
def customer_value(request):
    # Shows a pie chart containing customer value
    url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, url)
    return render(request, 'auditor/customer-value.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})

@login_required(login_url='login')
def complete_report(request):
    # Shows a complete report
    filter_url = reverse('api:filter', kwargs={'username' : request.user})
    filters = send_request(request, filter_url)
    return render(request, 'auditor/complete-report.html', {'base_url' : Tokens.BASE_URL, 'filters' : filters})


@login_required(login_url='login')
def get_product_volume(request, query):
    """
    This function will return a product volume JSON
    and this function is called inside javascript to 
    display pie chart in html page.
    """
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
    """
    This function will return a product value JSON
    and this function is called inside javascript to 
    display pie chart in html page.
    """
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
    """
    This function will return a customer volume JSON
    and this function is called inside javascript to 
    display pie chart in html page.
    """
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
    """
    This function will return a customer value JSON
    and this function is called inside javascript to 
    display pie chart in html page.
    """
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
    """
    This function will return a transactions JSON
    and this function is called inside javascript to 
    display pie chart in html page.
    """
    url = reverse('api:transactions')
    if query:
        transactions = send_request(request, url + '?' + query)
    else:
        transactions = send_request(request, url)
    return JsonResponse(transactions, safe=False)

def get_customer_dict(request, customer_dict):
    #Helper function to return a sorted dictoinary and called in multiple functions
    customers = send_request(request, reverse('api:customers'))
    new_dict = {}
    for i in customer_dict:
        for j in customers:
            if i == j['id']:
                new_dict[j['name']] = customer_dict[i]
    new_dict = {k:v for k, v in sorted(new_dict.items(), key=lambda x : x[1], reverse=True)}
    return new_dict

def send_request(request, url, params = None):
    """
    This functions sends a request to api app by taking an 
    url as a required argument and parameters as optional argument
    and depending on the arguments it will send a get request to
    passed url and if the access token is expired it will send 
    a request to refresh url and pass refresh token in header and 
    save new access token in cookie and then recursively call itself.
    """
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
                                        