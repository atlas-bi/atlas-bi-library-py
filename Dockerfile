# Optionally pass a DATABASE_URL and REDIS_URL arg
FROM python:3.11-alpine as python_install

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apk update \
    && apk add --no-cache build-base postgresql-dev gcc libxml2-dev libxslt-dev musl-dev libressl libffi-dev libressl-dev xmlsec-dev xmlsec unixodbc-dev openldap-dev

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN wget -O - https://install.python-poetry.org | python3 - \
 && chmod 755 ${POETRY_HOME}/bin/poetry \
 && poetry install --no-root --only main

FROM python:3.11-alpine as static
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE='atlas.settings.demo'

ARG DATABASE_URL \
    REDIS_URL

WORKDIR /app

COPY atlas ./atlas
COPY pyproject.toml ./
COPY --from=python_install /app/.venv ./.venv

WORKDIR /app/atlas

RUN [ -z "$REDIS_URL" ] \
 && apk add --no-cache redis

RUN if [ -z "$REDIS_URL" ]; then redis-server --daemonize yes; fi \
 && sleep 1 \
 && python manage.py collectstatic --no-input \
 && python manage.py compress --force -e html -e 'html.dj' \
 && python manage.py collectstatic --no-input \
 && python manage.py reset_db --no-input \
 && python manage.py migrate --run-syncdb \
 && python manage.py loaddata --app index initial demo/base demo/users demo/groups demo/user_roles demo/user_group_memberships demo/reports demo/report_docs demo/report_maint demo/report_frag_tags demo/terms demo/report_terms demo/report_hierarchy demo/report_query demo/user_folders demo/user_stars demo/shares

FROM python:3.11-alpine as deploy
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE='atlas.settings.demo'

WORKDIR /app

ARG DATABASE_URL \
    REDIS_URL

RUN apk update && apk add --no-cache openjdk11 bash lsof \
 && [ -z "$REDIS_URL" ] \
 && apk add --no-cache redis

COPY solr ./solr
COPY --from=static /app/atlas ./atlas
COPY pyproject.toml ./
COPY --from=python_install /app/.venv ./.venv

WORKDIR /app/atlas

CMD ls /app/solr; celery -A atlas worker -l DEBUG -E --detach && \
     if [ -z "$REDIS_URL" ]; then redis-server --daemonize yes; fi && \
    /app/solr/solr-9.0.0/bin/solr start -force -noprompt -v && gunicorn atlas.wsgi --workers 1 -b 0.0.0.0:$PORT --log-file -
