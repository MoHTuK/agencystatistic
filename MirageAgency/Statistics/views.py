from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from fake_useragent import UserAgent

from Statistics.models import Transaction
from django.shortcuts import render, redirect
from django.db.models import Q
import requests
import datetime
import pytz


def get_statistics_today(request):
    user = request.user
    timezone = pytz.timezone('Europe/Kiev')
    today = datetime.datetime.now(timezone)
    today_valid = today.strftime('%Y-%m-%d')
    login = user.username
    password = request.session.get('user_password', None)

    gifts_total = 0
    penalties_total = 0

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

    transaction_list = Transaction.objects.filter(Date__icontains=today_valid, Lady_ID=user.pk).order_by('-Date')

    gifts_list = Transaction.objects.filter(
        Q(Operation_type='GiftsDelivery') | Q(Operation_type='GiftsDeliverySatellite'), Lady_ID=user.pk,
        Date__icontains=today_valid)

    penalties_list = Transaction.objects.filter(Operation_type='Penalties', Lady_ID=user.pk,
                                                Date__icontains=today_valid)

    for i in gifts_list:
        gifts_total += i.Sum

    for i in penalties_list:
        penalties_total += i.Sum

    return transaction_list, total, lady_name, gifts_total, penalties_total


def get_statistics_date(request):
    user = request.user
    login = user.username
    password = request.session.get('user_password', None)

    api_url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=finances'

    gifts_total = 0
    penalties_total = 0

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

    gifts_list = Transaction.objects.filter(
        Q(Operation_type='GiftsDelivery') | Q(Operation_type='GiftsDeliverySatellite'), Lady_ID=user.pk,
        Date__icontains=date_selector)

    penalties_list = Transaction.objects.filter(Operation_type='Penalties', Lady_ID=user.pk,
                                                Date__icontains=date_selector)

    for i in gifts_list:
        gifts_total += i.Sum

    for i in penalties_list:
        penalties_total += i.Sum

    return transaction_list, total, lady_name, date_selector, gifts_total, penalties_total


def get_statistics_interval(request):
    user = request.user
    login = user.username
    password = request.session.get('user_password', None)

    api_url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=finances'

    start_date_str = request.POST['start_date']
    end_date_str = request.POST['end_date']

    gifts_total = 0
    penalties_total = 0


    data = {
        "login": login,
        "pass": password,
        "ladyID": login,
        "from": start_date_str,
        "to": end_date_str
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
    transaction_list = Transaction.objects.filter(Date__gte=start_date_str, Date__lte=end_date_str,
                                                  Lady_ID=user.pk).order_by('-Date')

    gifts_list = Transaction.objects.filter(
        Q(Operation_type='GiftsDelivery') | Q(Operation_type='GiftsDeliverySatellite'), Lady_ID=user.pk,
        Date__gte=start_date_str, Date__lte=end_date_str)

    penalties_list = Transaction.objects.filter(Operation_type='Penalties', Lady_ID=user.pk,
                                                Date__gte=start_date_str, Date__lte=end_date_str)

    for i in gifts_list:
        gifts_total += i.Sum

    for i in penalties_list:
        penalties_total += i.Sum

    return transaction_list, total, lady_name, start_date_str, end_date_str, gifts_total, penalties_total


@login_required(login_url='login')
def statistics(request):

    custom_admin_user_list = [920777, 918761, 918562, 900441, 912504, 920011, 914887, 913993, 878637, 917531, 916712,
                              919673, 919395, 903279, 906192, 901480, 917537, 904524, 899701, 912607, 915089, 913075,
                              917416, 914489, 893557, 917534, 883002, 832730, 899218, 851946, 895429, 895430]
    user = int(request.user.username)

    timezone = pytz.timezone('Europe/Kiev')
    today = datetime.datetime.now(timezone)
    today_valid = today.strftime('%Y-%m-%d')

    tomorrow = today + datetime.timedelta(days=1)
    tomorrow_valid = tomorrow.strftime('%Y-%m-%d')

    result = get_statistics_today(request)
    transaction_list = result[0]
    total = result[1]
    lady_name = request.user.first_name
    gifts_total = result[3]
    total_without_gifts = round(total - gifts_total, 1)
    penalties = result[4]
    total_without_penalties = round(total + penalties, 1)

    print(user)

    if request.method == 'POST' and request.POST.get('start_date') and request.POST.get('end_date'):
        result = get_statistics_interval(request)
        transaction_list = result[0]
        total = result[1]
        lady_name = request.user.first_name
        start_date = result[3]
        end_date = result[4]
        gifts_total = result[5]
        total_without_gifts = round(total - gifts_total, 1)
        penalties = result[6]
        total_without_penalties = round(total + penalties, 1)

        return render(request, 'Statistics/main.html',
                      context={'transaction_list': transaction_list, 'total': total, 'lady_name': lady_name,
                               'max_date': tomorrow_valid, 'start_date': start_date, 'end_date': end_date,
                               'gifts_total': gifts_total, 'total_without_gifts': total_without_gifts,
                               'total_without_penalties': total_without_penalties, 'penalties': penalties,
                               'custom_list': custom_admin_user_list, 'user': user})

    if request.method == 'POST' and request.POST.get('selected_date'):
        result = get_statistics_date(request)
        transaction_list = result[0]
        total = result[1]
        lady_name = request.user.first_name
        today_date = result[3]
        gifts_total = int(result[4])
        total_without_gifts = round(total - gifts_total, 1)
        penalties = result[5]
        total_without_penalties = round(total + penalties, 1)

        return render(request, 'Statistics/main.html',
                      context={'transaction_list': transaction_list, 'total': total, 'lady_name': lady_name,
                               'max_date': tomorrow_valid, 'today_date': today_date, 'gifts_total': gifts_total,
                               'total_without_gifts': total_without_gifts,
                               'total_without_penalties': total_without_penalties, 'penalties': penalties,
                               'custom_list': custom_admin_user_list, 'user': user})

    return render(request, 'Statistics/main.html',
                  context={'transaction_list': transaction_list, 'total': total, 'lady_name': lady_name,
                           'max_date': tomorrow_valid, 'gifts_total': gifts_total,
                           'total_without_gifts': total_without_gifts, 'penalties': penalties,
                           'total_without_penalties': total_without_penalties, 'custom_list': custom_admin_user_list,
                           'user': user})


def login_request(request):
    base_url = 'https://goldenbride.net'
    login_url = f'{base_url}/goldenbride/services/login'
    login_data = {
        'username': request.user.username,
        'userpass': request.POST.get('password'),
    }

    user_agent = UserAgent()
    random_user_agent = user_agent.random

    session = requests.Session()
    session.headers.update({'User-Agent': random_user_agent})

    # Аутентификация
    response = session.post(login_url, data=login_data)

    if response.ok:
        # Сохранение кукис в Django session
        request.session['web_cookies'] = requests.utils.dict_from_cookiejar(session.cookies)
        request.session['user_agent'] = random_user_agent  # Сохранение User-Agent

    return session


def login_view(request):

    if request.user.is_authenticated:
        return redirect('statistics')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            request.session['user_password'] = request.POST['password']
            login(request, form.get_user())
            return redirect('statistics')
    form = AuthenticationForm()
    return render(request, 'Statistics/login.html', context={'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
