# Use the Apache Airflow image as the base image
FROM apache/airflow:latest

# Switch to the root user to install system packages
USER root

# Install essential packages
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
ARG CHROME_VERSION="google-chrome-stable"
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install \
    ${CHROME_VERSION:-google-chrome-stable} \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Install ChromeDriver
RUN LATEST=$(wget -q -O - http://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget http://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

# Ajouter ces lignes après l'installation de ChromeDriver
# Créer un répertoire pour le profil Chrome
RUN mkdir -p /opt/airflow/chrome_profile && \
    chown -R airflow: /opt/airflow/chrome_profile

# Définir un volume pour persister le profil Chrome
VOLUME /opt/airflow/chrome_profile

# Copy project files and set ownership
COPY . /home/site/wwwroot
RUN chown -R airflow: /home/site/wwwroot

# Switch back to the airflow user
USER airflow

# Install Python packages from requirements.txt
RUN pip install -r /home/site/wwwroot/requirements.txt
