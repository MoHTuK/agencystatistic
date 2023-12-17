from celery.result import AsyncResult
from django.http import JsonResponse
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
    # headles mode
    options.add_argument('--headless=new')
    # Webdriver mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
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
        time.sleep(10)
        # login auth
        login = user.username
        login_input = driver.find_element(By.ID, 'login')
        login_input.clear()
        login_input.send_keys(str(login))
        time.sleep(1)
        # pass auth
        password = request.session.get('user_password', None)
        password_input = driver.find_element(By.ID, 'pass')
        password_input.clear()
        password_input.send_keys(str(password))
        password_input.send_keys(Keys.ENTER)
        time.sleep(10)

        menu_item = driver.find_element(By.CLASS_NAME, 'menu-item.bordered')
        all_options = menu_item.find_elements(By.TAG_NAME, 'a')
        driver.execute_script("arguments[0].click();", all_options[2])
        time.sleep(10)

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
    password = request.session.get('user_password', None)
    username = request.user.username
    task = get_online_id.delay(username, password)
    task_id = task.id
    driver = get_driver()

    if request.method == 'POST':
        online_userd_id = AsyncResult(task_id)
        url = 'https://goldenbride.net/'
        user = request.user
        driver.maximize_window()

        try:
            driver.get(url)
            login_button = driver.find_element(By.CLASS_NAME, 'logged-in')
            login_button.click()
            time.sleep(10)
            # login auth
            login = user.username
            login_input = driver.find_element(By.ID, 'login')
            login_input.clear()
            login_input.send_keys(str(login))
            time.sleep(1)
            # pass auth
            password = request.session.get('user_password', None)
            password_input = driver.find_element(By.ID, 'pass')
            password_input.clear()
            password_input.send_keys(str(password))
            password_input.send_keys(Keys.ENTER)
            time.sleep(10)

            mailbox_button = driver.find_element(By.CLASS_NAME, 'mail-linkLeftMenu')
            driver.execute_script("arguments[0].click();", mailbox_button)

            create_mail_button = driver.find_element(By.CLASS_NAME, 'create-email')
            driver.execute_script("arguments[0].click();", create_mail_button)

            input_divs = driver.find_elements(By.CLASS_NAME, 'search-girl.cleared')
            man_id_input = input_divs[1].find_element(By.CLASS_NAME, 'gwt-TextBox')
            man_id_input.clear()
            man_id_input.send_keys('man id')
            search_green_button = input_divs[1].find_element(By.CLASS_NAME, 'green-btn')
            driver.execute_script("arguments[0].click();", search_green_button)
            textarea = driver.find_element(By.TAG_NAME, 'textarea')
            textarea.send_keys('my msg')
            form_with_button = driver.find_element(By.CLASS_NAME, 'reply-form')
            send_button = form_with_button.find_element(By.CLASS_NAME, 'gwt-Button')
            driver.execute_script("arguments[0].click();", send_button)
            succsec_div = driver.find_element(By.CLASS_NAME, 'info-in')
            succsec_button = succsec_div.find_element(By.CLASS_NAME, 'green-btn')
            driver.execute_script("arguments[0].click();", succsec_button)




        except Exception as ex:
            print(ex)
        finally:
            driver.close()
            driver.quit()

    return render(request, 'LetterSender/sender.html', context={'task_id': task_id})


def task_status(request, task_id):
    task_result = AsyncResult(task_id)
    return JsonResponse({'status': task_result.status, 'result': task_result.result})


def main_sender_view(request):
    all_imgs = LadyPhoto.objects.filter(Lady_ID__username=request.user.username)
    driver = get_driver()


    return render(request, 'LetterSender/sender.html', context={'all_imgs': all_imgs})
