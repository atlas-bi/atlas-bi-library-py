FROM python:3.8

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update -qq \
     && apt-get install -yqq --no-install-recommends apt-utils curl pkg-config postgresql-contrib build-essential openjdk-11-jdk wget lsof unixodbc-dev unixodbc libpq-dev htop node npm node-gyp \
     && apt-get clean \
     && apt-get autoclean \
     && rm -rf /var/lib/apt/lists/*

RUN wget https://archive.apache.org/dist/lucene/solr/8.8.2/solr-8.8.2.tgz \
    && tar xzf solr-8.8.2.tgz solr-8.8.2/bin/install_solr_service.sh --strip-components=2 \
    && bash ./install_solr_service.sh solr-8.8.2.tgz \
    && rm solr-8.8.2.tgz

COPY /solr/solr.in.sh /etc/default/solr.in.sh

# disable swappiness and autoschema
RUN echo 'vm.swappiness = 1' >> /etc/sysctl.conf \
    && /opt/solr/bin/solr start -force -noprompt -v \
    # primary search core
    && /opt/solr/bin/solr create -c atlas -force \
    && /opt/solr/bin/solr config -c atlas -p 8983 -action set-user-property -property update.autoCreateFields -value false \
    # lookup search core
    && /opt/solr/bin/solr create -c atlas_lookups -force \
    && /opt/solr/bin/solr config -c atlas_lookups -p 8983 -action set-user-property -property update.autoCreateFields -value false

# copy solr atlas config
COPY /solr/atlas/managed-schema /var/solr/data/atlas/conf/managed-schema
COPY /solr/atlas/solrconfig.xml /var/solr/data/atlas/conf/solrconfig.xml
COPY /solr/atlas/synonyms.txt /var/solr/data/atlas/conf/synonyms.txt

# copy solr atlas lookup config
COPY /solr/atlas_lookups/managed-schema /var/solr/data/atlas_lookups/conf/managed-schema
COPY /solr/atlas_lookups/solrconfig.xml /var/solr/data/atlas_lookups/conf/solrconfig.xml
COPY /solr/atlas_lookups/synonyms.txt /var/solr/data/atlas_lookups/conf/synonyms.txt

WORKDIR /app

COPY /atlas/requirements.txt .

RUN pip install -r requirements.txt \
    && pip install gunicorn

COPY /atlas .

COPY release_tasks.sh .

CMD DJANGO_SETTINGS_MODULE='atlas.settings.demo' celery -A atlas worker -l DEBUG -E --detach && \
    /opt/solr/bin/solr start -force -noprompt -v && gunicorn atlas.wsgi-demo --workers 1 -b 0.0.0.0:$PORT --log-file -

# heroku container: login
# docker docker build   . -t atlas-py-test
# docker run -i -t -p 8000:8000 -e PORT=8000 -u 0 atlas-py-test
# heroku container:push web --app HEROKU_APP_NAME
# heroku container:release web --app HEROKU_APP_NAME