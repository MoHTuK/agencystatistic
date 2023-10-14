from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from Statistics.models import Transaction
from django.shortcuts import render, redirect
import requests
import datetime


def get_statistics_today(request):
    user = request.user
    today = datetime.date.today()
    today_valid = today.strftime('%Y-%m-%d')
    login = user.username
    password = request.session.get('user_password', None)

    api_url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=finances'

    data = {
        "login": login,
        "pass": password,
        "ladyID": login,
        "from": today_valid,
        "to": today_valid
    }
    response = requests.post(api_url, data=data)
    response_data = response.json()
    total = response_data['total']
    lady_name = response_data['list'][0]['name']
    for transaction in response_data["list"]:
        if Transaction.objects.filter(Date=transaction['date'], Lady_ID__username=transaction['ladyID']):
            continue
        else:
            transaction_data = Transaction(
                Lady_ID=user,
                Man_ID=transaction['userID'],
                Sum=transaction['sum'],
                Operation_type=transaction['operation'],
                Date=transaction['date'],
            )
            transaction_data.save()

    transaction_list = Transaction.objects.filter(Date__icontains=today_valid, Lady_ID=user.pk).order_by('-Date')
    return transaction_list, total, lady_name


def get_statistics_date(request):
    user = request.user
    login = user.username
    password = request.session.get('user_password', None)

    api_url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=finances'

    date_selector = request.POST.get('selected_date')
    data = {
        "login": login,
        "pass": password,
        "ladyID": login,
        "from": date_selector,
        "to": date_selector
    }
    response = requests.post(api_url, data=data)
    response_data = response.json()
    total = response_data['total']
    try:
        lady_name = response_data['list'][0]['name']
    except:
        lady_name = ''
    for transaction in response_data["list"]:
        if Transaction.objects.filter(Date=transaction['date'], Lady_ID__username=transaction['ladyID']):
            continue
        else:
            transaction_data = Transaction(
                Lady_ID=user,
                Man_ID=transaction['userID'],
                Sum=transaction['sum'],
                Operation_type=transaction['operation'],
                Date=transaction['date'],
            )
            transaction_data.save()
    transaction_list = Transaction.objects.filter(Date__icontains=date_selector, Lady_ID=user.pk).order_by('-Date')
    return transaction_list, total, lady_name, date_selector


def get_statistics_interval(request):
    user = request.user
    login = user.username
    password = request.session.get('user_password', None)

    api_url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=finances'

    start_date_str = request.POST['start_date']
    end_date_str = request.POST['end_date']

    end_date_first = datetime.date.fromisoformat(end_date_str)
    start_date = datetime.date.fromisoformat(start_date_str)
    end_date = datetime.date.fromisoformat(end_date_str) + datetime.timedelta(days=1)

    data = {
        "login": login,
        "pass": password,
        "ladyID": login,
        "from": start_date,
        "to": end_date
    }
    response = requests.post(api_url, data=data)
    response_data = response.json()
    total = response_data['total']
    try:
        lady_name = response_data['list'][0]['name']
    except:
        lady_name = ''
    for transaction in response_data["list"]:
        if Transaction.objects.filter(Date=transaction['date'], Lady_ID__username=transaction['ladyID']):
            continue
        else:
            transaction_data = Transaction(
                Lady_ID=user,
                Man_ID=transaction['userID'],
                Sum=transaction['sum'],
                Operation_type=transaction['operation'],
                Date=transaction['date'],
            )
            transaction_data.save()
    transaction_list = Transaction.objects.filter(Date__gte=start_date, Date__lte=end_date,
                                                  Lady_ID=user.pk).order_by('-Date')
    return transaction_list, total, lady_name, start_date, end_date_first


def statistics(request):
    today = datetime.date.today()
    today_valid = today.strftime('%Y-%m-%d')

    result = get_statistics_today(request)
    transaction_list = result[0]
    total = result[1]
    lady_name = result[2]

    if request.method == 'POST' and request.POST.get('start_date') and request.POST.get('end_date'):
        result = get_statistics_interval(request)
        transaction_list = result[0]
        total = result[1]
        lady_name = result[2]
        start_date = result[3]
        end_date = result[4]

        return render(request, 'statistics/main.html',
                      context={'transaction_list': transaction_list, 'total': total, 'lady_name': lady_name,
                               'max_date': today_valid, 'start_date': start_date, 'end_date': end_date})

    if request.method == 'POST' and request.POST.get('selected_date'):
        result = get_statistics_date(request)
        transaction_list = result[0]
        total = result[1]
        lady_name = result[2]
        today_date = result[3]

        return render(request, 'statistics/main.html',
                      context={'transaction_list': transaction_list, 'total': total, 'lady_name': lady_name,
                               'max_date': today_valid, 'today_date': today_date})

    return render(request, 'statistics/main.html',
                  context={'transaction_list': transaction_list, 'total': total, 'lady_name': lady_name,
                           'max_date': today_valid})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            request.session['user_password'] = request.POST['password']
            login(request, form.get_user())
            return redirect('statistics')
    form = AuthenticationForm()
    return render(request, 'statistics/login.html', context={'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
