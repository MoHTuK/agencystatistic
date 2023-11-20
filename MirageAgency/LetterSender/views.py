from celery.result import AsyncResult
from django.shortcuts import render
import re
import bs4
import time
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from LetterSender.models import LadyPhoto, ManAcc
from LetterSender.celery_tasks import get_online_id



def get_driver():
    useragent = UserAgent()
    options = webdriver.ChromeOptions()
    # User-agent
    options.add_argument(f"user-agent={useragent.random}")
    # Webdriver detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    # headles modegit
    options.add_argument('--headless=new')
    # Webdriver mode
    driver = webdriver.Chrome(options=options)
    return driver


def get_lady_imgs(request, driver):
    url = 'https://goldenbride.net/'
    user = request.user
    driver.maximize_window()

    try:
        driver.get(url)
        login_button = driver.find_element(By.CLASS_NAME, 'logged-in')
        login_button.click()
        time.sleep(2)

        # login auth
        login = user.username
        login_input = driver.find_element(By.ID, 'login')
        login_input.clear()
        login_input.send_keys(str(login))

        # pass auth
        password = request.session.get('user_password', None)
        password_input = driver.find_element(By.ID, 'pass')
        password_input.clear()
        password_input.send_keys(str(password))
        password_input.send_keys(Keys.ENTER)
        time.sleep(10)

        menu_item = driver.find_element(By.CLASS_NAME, 'menu-item.bordered')
        all_options = menu_item.find_elements(By.CLASS_NAME, 'gwt-Anchor')
        all_options[2].click()
        time.sleep(5)

        page_source = driver.page_source
        soup = bs4.BeautifulSoup(page_source, 'lxml')

        div_blocks = soup.find_all('div', class_='img-frame')

        for div in div_blocks:
            link = div.find('a', class_='gwt-Anchor')
            link_href = link.get('href')

            if LadyPhoto.objects.filter(Lady_ID__username=user.username, Img_url=link_href):
                continue
            else:
                img_data = LadyPhoto(
                    Img_url=link_href,
                    Lady_ID=user
                )
                img_data.save()

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def pars_imgs(request):
    get_lady_imgs(request, get_driver())
    return render(request, 'LetterSender/sender.html', context={})


def pars_id(request):
    all_id = get_online_id.delay(1, 2)
    status = all_id.status
    result = all_id.get()
    return render(request, 'LetterSender/sender.html', context={'all_id': status, 'result': result})


def main_sender_view(request):
    all_imgs = LadyPhoto.objects.filter(Lady_ID__username=request.user.username)
    # all_id = get_online_id(request, get_driver())
    return render(request, 'LetterSender/sender.html', context={'all_imgs': all_imgs})
