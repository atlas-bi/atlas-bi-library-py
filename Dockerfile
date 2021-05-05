# docker build . -t atlas-py-test
# docker run -i -t -p 8000:8000 -e PORT=8000 -u 0 atlas-py-test
FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    REMOTE=https://github.com/Riverside-Healthcare/Atlas-Py.git

RUN apt-get update -qq \
     && apt-get install -y --no-install-recommends apt-utils curl pkg-config postgresql postgresql-contrib > /dev/null  \
     && apt-get clean \
     && rm -rf /var/lib/apt/lists/*

RUN su - postgres -c "/etc/init.d/postgresql start && psql --command \"CREATE USER atlas WITH SUPERUSER PASSWORD '12345';\"&& createdb -O atlas atlas"

RUN apt-get install -y --no-install-recommends. \
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
    libmemcached-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git -c http.sslVerify=false clone --depth 1 "$REMOTE" . \
    && python -m pip install --disable-pip-version-check poetry \
    && poetry config virtualenvs.create false \
    && poetry install

WORKDIR /app/atlas

RUN /etc/init.d/postgresql start \
    && poetry run python manage.py migrate --run-syncdb  --settings atlas.settings.demo \
    && poetry run python manage.py loaddata index/fixtures/*.yaml --settings atlas.settings.demo


CMD (redis-server &) \
    && /etc/init.d/postgresql start \
    && poetry run python manage.py runserver 0.0.0.0:$PORT --settings atlas.settings.demo
