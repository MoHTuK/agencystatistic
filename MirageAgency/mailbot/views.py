import json
import time

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render, redirect
from fake_useragent import UserAgent
from .forms import *
from .models import *
from django.http import JsonResponse, HttpResponse
import requests


def login_request(request):
    base_url = 'https://goldenbride.net'
    login_url = f'{base_url}/goldenbride/services/login'

    login_data = {
        'username': request.user.username,
        'userpass': request.session.get('user_password', None),
    }

    session = requests.Session()
    user_agent = UserAgent().random
    session.headers.update({'User-Agent': user_agent})

    while True:
        response = session.post(login_url, data=login_data)
        if response.status_code == 200:
            return session
        elif response.status_code == 429:
            print("Rate limit reached. Waiting for 4 seconds...")
            time.sleep(4)  # Пауза на 4 секунды, как рекомендует API
        else:
            print(f"Login failed with status code {response.status_code} and message {response.text}")
            raise Exception("Failed to login")


def get_session_key(username):
    return f"api_session_{username}"


def store_session(username, session):
    cache.set(get_session_key(username), session, timeout=settings.SESSION_COOKIE_AGE)


def retrieve_session(username):
    return cache.get(get_session_key(username))


def login_and_store_session(username, request):
    session = login_request(request)
    store_session(username, session)
    return session

def clear_session(username):
    cache_key = get_session_key(username)
    cache.delete(cache_key)



def proxy_send_msg(request):
    session = retrieve_session(request.user.username)

    login = request.user.username
    password = request.session.get('user_password', None)

    data = {
        "login": login,
        "pass": password,
    }

    if not session:
        # Если сессия не найдена, выполнить логин и сохранить сессию
        session = login_and_store_session(request.user.username, request)

    online_url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=online'

    if request.method == 'POST':

        recipient_group = request.POST.get('recipient_group')
        message_text = request.POST.get('messageText')
        selected_photos = request.POST.getlist('selected_photos')
        filtered_man_id_list = []

        if recipient_group == 'online_men':
            man_id_blacklist = Blacklist.objects.filter(lady_id=request.user.pk).values_list('man_id', flat=True)
            man_id_response = requests.post(online_url, data=data).text
            man_id_list = json.loads(man_id_response)

            filtered_man_id_list = [man_id for man_id in man_id_list if man_id not in man_id_blacklist]

        elif recipient_group == 'goldman':

            man_id_blacklist = Blacklist.objects.filter(lady_id=request.user.pk).values_list('man_id', flat=True)
            man_id_list = GoldMan.objects.order_by('?')[:500].values_list('man_id', flat=True)

            filtered_man_id_list = [man_id for man_id in man_id_list if man_id not in man_id_blacklist]

        elif recipient_group == 'custom_list':
            custom_list_text = request.POST.get('customListText', '')
            str_filtered_man_id_list = [line.strip() for line in custom_list_text.splitlines() if line.strip()]
            filtered_man_id_list = list(map(int, str_filtered_man_id_list))

        url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=send&list={filtered_man_id_list}&text={message_text}'

        for i, photo in enumerate(selected_photos):
            if i < 2:  # Предположим, что максимум можно прикрепить два изображения
                url += f"&attach{i + 1}={photo}"

        print(url)
        print(f"{request.user.username} sending")
        print(session.headers)
        response = session.get(url)
        print(response.status_code, response.text)

        clear_session(login)
        return JsonResponse({'success': True, 'message': 'Рассылка запущена '})
    else:
        return JsonResponse({'success': False, 'message': 'Ошибка в данных формы'})


def proxy_status(request):
    print(f'{request.user.username} status check ')

    login = request.user.username
    password = request.session.get('user_password', None)

    data = {
        "login": login,
        "pass": password,
    }

    url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=status'
    response = requests.post(url, data=data)
    data = response.json()
    status = data['status']
    count = data.get('count', 0)

    return JsonResponse({'success': True, 'status': status, 'count': count})


def proxy_stop(request):
    print(f'{request.user.username} stop bot ')

    login = request.user.username
    password = request.session.get('user_password', None)

    data = {
        "login": login,
        "pass": password,
    }

    url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=stop'
    response = requests.post(url, data=data)
    data = response.json()
    status = data['status']

    return JsonResponse({'success': True, 'status': status})


def proxy_get_goldmen_list(request):
    goldmen_ids = list(GoldMan.objects.values_list('man_id', flat=True))

    return JsonResponse({'goldmen_ids': goldmen_ids})


def add_in_blacklist(request):
    form = BlacklistForm(request.POST)

    if form.is_valid():
        man_id = form.cleaned_data['man_id']
        lady_id = request.user

        if Blacklist.objects.filter(lady_id=lady_id, man_id=man_id).exists():
            return JsonResponse({'success': False, 'message': 'Этот пользователь уже в вашем черном списке'})

        blacklist_instance = form.save(commit=False)
        blacklist_instance.lady_id = lady_id
        blacklist_instance.save()
        return JsonResponse({'success': True, 'message': 'Пользователь успешно добавлен в черный список'})
    else:
        return JsonResponse({'success': False, 'message': 'Ошибка в данных формы'})


def add_in_goldman(request):
    form = GoldManForm(request.POST)
    if form.is_valid():
        man_id = form.cleaned_data['man_id']
        if GoldMan.objects.filter(man_id=man_id).exists():
            return JsonResponse({'success': False, 'message': 'Этот пользователь уже в списке платников'})

        goldman_list_instance = form.save()
        return JsonResponse({'success': True, 'message': 'Пользователь успешно добавлен в список платников'})
    else:
        return JsonResponse({'success': False, 'message': 'Ошибка в данных формы'})


@login_required(login_url='login')
def mailbot(request):
    session = login_and_store_session(request.user.username, request)
    base_url = 'https://goldenbride.net'

    user = request.user
    login = user.username
    password = request.session.get('user_password', None)

    data = {
        "login": login,
        "pass": password,
    }

    images_url = f'{base_url}/usermodule/services/agencyhelper?command=attach'
    images_url_response = requests.post(images_url, data=data)
    images_url_data = images_url_response.json()
    img_list = []

    for item in images_url_data['list']:
        img_list.append({"image_id": item["imageId"], 'image_url': item['imageUrls']['smallSizeUrl']})

    goldman_form = GoldManForm(request.POST)
    blacklist_form = BlacklistForm(request.POST)

    return render(request, 'mailbot/main.html', context={'img_list': img_list, 'goldman_form': goldman_form,
                                                         'blacklist_form': blacklist_form, 'user': user})
