#!/bin/bash
python manage.py flush --no-input --settings atlas.settings.demo
python manage.py migrate --run-syncdb  --settings atlas.settings.demo
python manage.py loaddata index/fixtures/*.yaml --settings atlas.settings.demo
# populate search
/opt/solr/bin/solr start -force -noprompt -v \
&& (celery worker -A atlas --loglevel=debug &) \
&& sleep 5 \
&& python python  manage.py  shell --command="import atlas; from etl.tasks.search import initiatives; initiatives.reset_initiatives.delay()" \
&& python python  manage.py  shell --command="import atlas; from etl.tasks.search import projects; projects.reset_projects.delay()" \
&& python python  manage.py  shell --command="import atlas; from etl.tasks.search import reports; reports.reset_reports.delay()" \
&& python python  manage.py  shell --command="import atlas; from etl.tasks.search import terms; terms.reset_terms.delay()"
