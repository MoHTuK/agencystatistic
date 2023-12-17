# Используйте образ Debian или Ubuntu
FROM ubuntu:latest

# Установка переменных для неинтерактивного режима и временной зоны
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Kiev
# Обновите список пакетов и установите необходимые зависимости
RUN apt-get update && apt-get install -y wget gnupg2 unzip

RUN wget https://www.slimjet.com/chrome/download-chrome.php?file=files%2F104.0.5112.102%2Fgoogle-chrome-stable_current_amd64.deb -O google-chrome.deb
RUN dpkg -i google-chrome.deb || apt-get install -fy

# Установите ChromeDriver (вы можете изменить версию на более подходящую)
RUN wget https://chromedriver.storage.googleapis.com/104.0.5112.79/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver
RUN apt-get install -y libglib2.0 libnss3 libgconf-2-4 libfontconfig1
RUN apt-get install -y python3-dev python3-pip libjpeg-dev libpq-dev zlib1g-dev
RUN python3 -V

COPY requirements.txt /temp/requirements.txt
COPY MirageAgency /MirageAgency
WORKDIR /MirageAgency
EXPOSE 8000

RUN apt-get install -y postgresql-client build-essential libpq-dev

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password agency-admin

USER agency-admin