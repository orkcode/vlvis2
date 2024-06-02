FROM dockerhub.timeweb.cloud/library/python:3.12.1-slim

RUN apt-get update && apt-get install -y make redis-server

RUN pip install pipenv

ENV APP_ROOT /app
WORKDIR ${APP_ROOT}

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --ignore-pipfile

COPY . ${APP_ROOT}

CMD ["gunicorn", "-c", "gunicorn.conf.py", "config.wsgi:application"]
