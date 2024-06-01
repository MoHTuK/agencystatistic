from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import *
from django.http import JsonResponse
import requests
import time


def login_request(request):
    base_url = 'https://goldenbride.net'
    login_url = f'{base_url}/goldenbride/services/login'

    login_data = {
        'username': request.user.username,
        'userpass': request.session.get('user_password', None),
    }

    session = requests.Session()

    login_response = session.post(login_url, data=login_data)
    return session, login_response


@login_required(login_url='login')
def proxy_online_man(request):

    url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=online'
    response = login_request(request)[0].get(url)
    return response.json()


def proxy_send_msg(request):
    base_url = 'https://goldenbride.net'
    login_url = f'{base_url}/goldenbride/services/login'

    login_data = {
        'username': request.user.username,
        'userpass': request.session.get('user_password', None),
    }

    session = requests.Session()

    login_response = session.post(login_url, data=login_data)

    man_id_list = proxy_online_man(request)
    if request.method == 'POST':
        message_text = request.POST.get('messageText')
        selected_photos = request.POST.getlist('selected_photos')
        url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=send&list={man_id_list}&text={message_text}'

        for i, photo in enumerate(selected_photos):
            if i < 2:  # Предположим, что максимум можно прикрепить два изображения
                url += f"&attach{i + 1}={photo}"

        session.get(url)
        time.sleep(5)
        return redirect('mailbot')


def add_in_blacklist(request):
    form = BlacklistForm(request.POST)
    if form.is_valid():
        blacklist_instance = form.save(commit=False)
        blacklist_instance.lady_id = request.user
        blacklist_instance.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})


def add_in_goldman(request):
    form = GoldManForm(request.POST)
    if form.is_valid():
        goldman_list_instance = form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})


@login_required(login_url='login')
def mailbot(request):
    base_url = 'https://goldenbride.net'
    login_url = f'{base_url}/goldenbride/services/login'

    login_data = {
        'username': request.user.username,
        'userpass': request.session.get('user_password', None),
    }

    session = requests.Session()

    login_response = session.post(login_url, data=login_data)

    images_url = f'{base_url}/usermodule/services/agencyhelper?command=attach'
    images_url_response = session.get(images_url)
    images_url_data = images_url_response.json()
    img_list = []

    for item in images_url_data['list']:
        img_list.append({"image_id": item["imageId"], 'image_url': item['imageUrls']['smallSizeUrl']})

    goldman_form = GoldManForm(request.POST)
    blacklist_form = BlacklistForm(request.POST)

    return render(request, 'mailbot/main.html', context={'img_list': img_list, 'goldman_form': goldman_form,
                                                         'blacklist_form': blacklist_form})

