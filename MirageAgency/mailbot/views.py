import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.http import JsonResponse, HttpResponse
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
    session.post(login_url, data=login_data)

    return session


# @login_required(login_url='login')
# def proxy_online_man(request):
#
#     session = login_request(request)
#
#     url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=online'
#     response = session.get(url)
#
#     return response.json()


def proxy_send_msg(request):

    session = login_request(request)

    online_url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=online'

    if request.method == 'POST':

        recipient_group = request.POST.get('recipient_group')
        message_text = request.POST.get('messageText')
        selected_photos = request.POST.getlist('selected_photos')
        filtered_man_id_list = []

        if recipient_group == 'online_men':
            man_id_blacklist = Blacklist.objects.filter(lady_id=request.user.pk).values_list('man_id', flat=True)
            man_id_response = session.get(online_url).text
            man_id_list = json.loads(man_id_response)

            filtered_man_id_list = [man_id for man_id in man_id_list if man_id not in man_id_blacklist]

        elif recipient_group == 'goldman':

            man_id_blacklist = Blacklist.objects.filter(lady_id=request.user.pk).values_list('man_id', flat=True)
            man_id_list = GoldMan.objects.order_by('?')[:600].values_list('man_id', flat=True)

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
        session.get(url)

        return JsonResponse({'success': True, 'message': 'Рассылка запущена '})
    else:
        return JsonResponse({'success': False, 'message': 'Ошибка в данных формы'})


def proxy_status(request):

    session = login_request(request)
    url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=status'
    response = session.get(url)
    data = response.json()
    status = data['status']
    count = data.get('count', 0)

    return JsonResponse({'success': True, 'status': status, 'count': count})


def proxy_stop(request):

    session = login_request(request)
    url = f'https://goldenbride.net/usermodule/services/agencyhelper?command=stop'
    response = session.get(url)
    data = response.json()
    status = data['status']

    return JsonResponse({'success': True, 'status': status})


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
    base_url = 'https://goldenbride.net'
    login_url = f'{base_url}/goldenbride/services/login'

    user = request.user

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
                                                         'blacklist_form': blacklist_form, 'user': user})

