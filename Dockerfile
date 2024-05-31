FROM dockerhub.timeweb.cloud/library/python:3.11-slim-buster

RUN apt-get update && apt-get install -y make redis-server curl

# Установка pyenv
RUN curl https://pyenv.run | bash

# Добавление pyenv в PATH
ENV PATH="/root/.pyenv/bin:/root/.pyenv/shims:${PATH}"

# Установка Python 3.12.1 через pyenv
RUN pyenv install 3.12.1 && pyenv global 3.12.1

RUN pip install pipenv

ENV APP_ROOT /app
WORKDIR ${APP_ROOT}

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --ignore-pipfile

COPY . ${APP_ROOT}

CMD ["gunicorn", "-c", "gunicorn.conf.py", "config.wsgi:application"]
