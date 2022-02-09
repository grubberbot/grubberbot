# syntax=docker/dockerfile:1

FROM ubuntu:20.04 AS base
WORKDIR /usr/src/app

# Update
RUN apt-get -y update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get install -y git vim

# Install python and pip packages
RUN apt-get install -y python3.8 python3-pip
RUN python3.8 -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN python3.8 -m pip install --upgrade -r requirements.txt

# Install Google Chrome
RUN apt install wget
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb

# Install discord from the dev branch
RUN git clone https://github.com/Rapptz/discord.py
WORKDIR /usr/src/app/discord.py
RUN python3.8 -m pip install -U .[voice]
WORKDIR /usr/src/app

FROM base AS test
CMD ["python3.8", "-m", "unittest", "discover", "-v"]

FROM base AS develop
CMD ["python3.8", "develop.py"]

FROM base AS production
CMD ["python3.8", "bot.py"]
