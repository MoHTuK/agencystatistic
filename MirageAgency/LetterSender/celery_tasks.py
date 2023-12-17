from MirageAgency.celery import app

import re
import bs4
import time
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


@app.task
def get_online_id(username, password):
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

    url = 'https://goldenbride.net/'
    driver.maximize_window()
    all_id = []

    try:
        driver.get(url)
        login_button = driver.find_element(By.CLASS_NAME, 'logged-in')
        login_button.click()
        time.sleep(2)

        # login auth
        login = username
        login_input = driver.find_element(By.ID, 'login')
        login_input.clear()
        login_input.send_keys(str(login))

        # pass auth
        password = password
        password_input = driver.find_element(By.ID, 'pass')
        password_input.clear()
        password_input.send_keys(str(password))
        password_input.send_keys(Keys.ENTER)
        time.sleep(10)

        menu_item = driver.find_element(By.CLASS_NAME, 'menu-item')

        all_options = menu_item.find_elements(By.TAG_NAME, 'a')
        driver.execute_script("arguments[0].click();", all_options[3])
        time.sleep(5)

        while True:
            try:
                page_source = driver.page_source
                soup = bs4.BeautifulSoup(page_source, 'lxml')
                profile_count = soup.find_all('div', class_='profile-item')
                user_id = soup.find_all('span', class_='id', string=re.compile(r'(?<!pub)ID:'))
                for item in user_id:
                    all_id.append(item.text.lstrip('ID: '))
                if len(profile_count) < 12:
                    break
                next_button = driver.find_element(By.CSS_SELECTOR, '.pagination.paging-right .next')
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(0.3)

            except Exception as ex:
                print(ex)
                break

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
    return all_id
