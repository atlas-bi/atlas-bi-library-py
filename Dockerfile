FROM python:3.8

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update -qq \
     && apt-get install -yqq --no-install-recommends apt-utils curl pkg-config postgresql-contrib build-essential openjdk-11-jdk wget lsof \
     && apt-get clean \
     && apt-get autoclean

RUN wget https://archive.apache.org/dist/lucene/solr/8.8.2/solr-8.8.2.tgz \
    && tar xzf solr-8.8.2.tgz solr-8.8.2/bin/install_solr_service.sh --strip-components=2 \
    && bash ./install_solr_service.sh solr-8.8.2.tgz \
    && rm solr-8.8.2.tgz

COPY /solr/solr.in.sh /etc/default/solr.in.sh

# disable swappiness and autoschema
RUN echo 'vm.swappiness = 1' >> /etc/sysctl.conf \
    && su solr -c "/opt/solr/bin/solr start -noprompt -v "  \
    && su solr -c "/opt/solr/bin/solr create -c atlas" \
    && su solr -c "/opt/solr/bin/solr config -c atlas -action set-user-property -property update.autoCreateFields -value false" \

# copy solr config
COPY /solr /var/solr/data/atlas/conf/.

WORKDIR /app
COPY /atlas .

CMD su solr -c "/opt/solr/bin/solr start -noprompt -v"  && python -m manage.py runserver
