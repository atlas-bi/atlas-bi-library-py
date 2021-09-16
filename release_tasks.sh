#!/bin/bash
npm install
npm run build
python manage.py flush --no-input --settings atlas.settings.demo
python manage.py migrate --run-syncdb  --settings atlas.settings.demo
python manage.py loaddata index/fixtures/*.yaml --settings atlas.settings.demo
# populate search. this will no longer be needed
# after save events are added, as loaddata triggers those events.
# will still need to start solr before load data however.
/opt/solr/bin/solr start -force -noprompt -v
sleep 5s
export DJANGO_SETTINGS_MODULE="atlas.settings.demo"
python  manage.py  shell --command="import atlas; from etl.tasks.search import initiatives; initiatives.reset_initiatives()"
python  manage.py  shell --command="import atlas; from etl.tasks.search import collections; collection.reset_collections()"
python  manage.py  shell --command="import atlas; from etl.tasks.search import reports; reports.reset_reports()"
python  manage.py  shell --command="import atlas; from etl.tasks.search import terms; terms.reset_terms()"
