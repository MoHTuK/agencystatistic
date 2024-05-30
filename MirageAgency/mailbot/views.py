from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
# Create your views here.


@login_required(login_url='login')
def mailbot(request):
    # Base URL
    base_url = 'https://goldenbride.net'
    # Login URL
    login_url = f'{base_url}/goldenbride/services/login'


    login_data = {
        'username': request.user.username,
        'userpass': request.session.get('user_password', None),
    }
    session = requests.Session()
    login_response = session.post(login_url, data=login_data)
    images_url = f'{base_url}/usermodule/services/agencyhelper?command=attach'
    images_url_response = session.get(images_url).json()
    img_list = []
    for item in images_url_response['list']:
        img_list.append({"image_id": item["imageId"], 'image_url': item['imageUrls']['smallSizeUrl']})

    return render(request, 'mailbot/main.html', context={'img_list': img_list})
