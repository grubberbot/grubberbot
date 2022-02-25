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

# Add a user for running applications.
RUN useradd apps
RUN mkdir -p /home/apps && chown apps:apps /home/apps

# Install x11vnc.
RUN apt-get install -y x11vnc
# Install xvfb.
RUN apt-get install -y xvfb
# Install fluxbox.
RUN apt-get install -y fluxbox
# Install wget.
RUN apt-get install -y wget
# Install wmctrl.
RUN apt-get install -y wmctrl
# Set the Chrome repo.
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
# Install Chrome.
RUN apt-get update && apt-get -y install google-chrome-stable

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
