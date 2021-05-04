FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    REMOTE=https://github.com/Riverside-Healthcare/Atlas-Py.git

RUN apt-get update -qq \
     && apt-get install -y -qq --no-install-recommends apt-utils curl pkg-config postgresql postgresql-contrib > /dev/null

RUN su - postgres -c "/etc/init.d/postgresql start && psql --command \"CREATE USER atlas WITH SUPERUSER PASSWORD '12345';\"&& createdb -O atlas atlas"

RUN apt-get install -y -qq \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl \
    git \
    wget \
    libldap2-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    unixodbc \
    unixodbc-dev \
    libpq-dev \
    libsqlite3-0 \
    libsasl2-dev \
    libxml2-dev \
    libxmlsec1-dev \
    redis-server \
    memcached \
    libmemcached-tools

WORKDIR /app

RUN git -c http.sslVerify=false clone --depth 1 "$REMOTE" . \
    && python -m pip install --disable-pip-version-check poetry \
    && poetry config virtualenvs.create false \
    && poetry install \
    && poetry env info

RUN cd atlas; \
    /etc/init.d/postgresql start \
    && poetry run python manage.py migrate --run-syncdb --database default --settings atlas.settings.demo \
    && poetry run python manage.py loaddata index/fixtures/*.yaml --settings atlas.settings.demo


CMD (redis-server &) && (/etc/init.d/postgresql start &) &&  cd atlas; poetry run python manage.py runserver 0.0.0.0:$PORT --settings atlas.settings.demo
