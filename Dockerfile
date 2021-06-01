FROM python:3.8

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update -qq \
     && apt-get install -yqq --no-install-recommends apt-utils curl pkg-config postgresql-contrib build-essential openjdk-11-jdk wget lsof unixodbc-dev unixodbc libpq-dev \
     && apt-get clean \
     && apt-get autoclean

RUN wget https://archive.apache.org/dist/lucene/solr/8.8.2/solr-8.8.2.tgz \
    && tar xzf solr-8.8.2.tgz solr-8.8.2/bin/install_solr_service.sh --strip-components=2 \
    && bash ./install_solr_service.sh solr-8.8.2.tgz \
    && rm solr-8.8.2.tgz

COPY /solr/solr.in.sh /etc/default/solr.in.sh

# disable swappiness and autoschema
RUN echo 'vm.swappiness = 1' >> /etc/sysctl.conf \
    && /opt/solr/bin/solr start -force -noprompt -v \
    && /opt/solr/bin/solr create -c atlas -force \
    && /opt/solr/bin/solr config -c atlas -p 8983 -action set-user-property -property update.autoCreateFields -value false

# copy solr config
COPY /solr /var/solr/data/atlas/conf/.

WORKDIR /app

COPY /atlas/requirements.txt .

RUN pip install -r requirements.txt \
    && pip install gunicorn

COPY /atlas .

CMD /opt/solr/bin/solr start -force -noprompt -v && gunicorn atlas.wsgi-demo --workers 4 -b 0.0.0.0:$PORT --log-file -

# docker docker build   . -t atlas-py-test
# docker run -i -t -p 8000:8000 -e PORT=8000 -u 0 atlas-py-test