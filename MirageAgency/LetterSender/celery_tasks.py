import re
import bs4
import time

from celery import shared_task
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from MirageAgency.celery import app


@shared_task
def get_online_id(username, password):
    all_id = [username, password]
    return all_id
