#!/bin/bash
python manage.py flush --no-input --settings atlas.settings.demo
python manage.py migrate --run-syncdb  --settings atlas.settings.demo
python manage.py loaddata index/fixtures/*.yaml --settings atlas.settings.demo
# populate search. this will no longer be needed
# after save events are added, as loaddata triggers those events.
# will still need to start solr& celery before load data however.
/opt/solr/bin/solr start -force -noprompt -v \
&& (DJANGO_SETTINGS_MODULE='atlas.settings.dev' poetry run celery -A atlas worker -l DEBUG -E &) \
&& sleep 5 \
&& python python  manage.py  shell --command="import atlas; from etl.tasks.search import initiatives; initiatives.reset_initiatives.delay()" \
&& python python  manage.py  shell --command="import atlas; from etl.tasks.search import projects; projects.reset_projects.delay()" \
&& python python  manage.py  shell --command="import atlas; from etl.tasks.search import reports; reports.reset_reports.delay()" \
&& python python  manage.py  shell --command="import atlas; from etl.tasks.search import terms; terms.reset_terms.delay()"
