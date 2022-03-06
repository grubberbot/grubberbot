# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster AS base

WORKDIR /app

# Upgrade pip and build
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade build

# Install requirements
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

COPY . .
RUN python3 -m build
RUN python3 -m pip install -e . --no-deps

FROM base AS dev
CMD ["python3", "dev.py"]

FROM base AS test
RUN python3 -m pip install -r requirements-dev.txt
CMD ["pytest"]

FROM base AS bot
CMD ["python3 app.py"]
