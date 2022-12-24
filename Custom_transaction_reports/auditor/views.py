from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
import requests
from django.http import HttpResponse

# Create your views here.
class Tokens:
    token = ''
    refresh = ''

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
        url = 'http://127.0.0.1:8000/api/login'
        details = {
            "username": username,
            "password": password
        }
        data = requests.post(url = url, data=details)
        if data.status_code == 200:
            data = data.json()
            user = User.objects.get(username = username)
            Tokens.token = data['token']['access']
            Tokens.refresh = data['token']['refresh']
            login(request, user)
            return redirect('dashboard')
        
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        url = 'http://127.0.0.1:8000/api/register'
        details = {
            "username": username,
            "email": email,
            "password": password
        }
        data = requests.post(url = url, data = details)
        if data.status_code == 201:
            data = data.json()
            user = User.objects.get(username = username)
            Tokens.token = data['token']['access']
            Tokens.refresh = data['token']['refresh']
            login(request, user)
            return redirect('dashboard')

def dashboard(request):
    url = 'http://127.0.0.1:8000/api/transaction'
    data = send_request(request, url)
    return render(request, 'auditor/dashboard-dashboard.html', {'data' : data[:-11:-1]})

def transactions(request):
    pass

def filters(request):
    url = f'http://127.0.0.1:8000/api/filter/{request.user}'
    data = send_request(request, url)
    return render(request, 'auditor/filters-dashboard.html', {'filters' : data})

def send_request(request, url):
    data = requests.get(url =url, headers={'authorization':f'Bearer {Tokens.token}', 'content-type': 'application/json'})
    if data.status_code == 200:
        return data.json()
    if data.status_code == 401:
        get_new_token(request)
        return send_request(request,url)

def get_new_token(request):
    url = 'http://127.0.0.1:8000/api/token/refresh/'
    data = requests.post(url = url, data = {"refresh": Tokens.refresh})
    Tokens.token = data.json()['access']
                                        