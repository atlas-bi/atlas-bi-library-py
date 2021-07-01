/opt/solr/bin/solr create -c atlas
#/opt/solr/bin/solr -c atlas -p 8983 -action set-user-property -property update.autoCreateFields -value false; \

/opt/solr/bin/solr create -c atlas_lookups
#/opt/solr/bin/solr -c atlas_lookups -p 8983 -action set-user-property -property update.autoCreateFields -value false; \

cp /var/solr/mine/atlas/managed-schema /var/solr/data/atlas/conf/managed-schema
cp /var/solr/mine/atlas/solrconfig.xml /var/solr/data/atlas/conf/solrconfig.xml
cp /var/solr/mine/atlas/synonyms.txt /var/solr/data/atlas/conf/synonyms.txt

curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=atlas"

cp /var/solr/mine/atlas_lookups/managed-schema /var/solr/data/atlas_lookups/conf/managed-schema
cp /var/solr/mine/atlas_lookups/solrconfig.xml /var/solr/data/atlas_lookups/conf/solrconfig.xml
cp /var/solr/mine/atlas_lookups/synonyms.txt /var/solr/data/atlas_lookups/conf/synonyms.txt

curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=atlas_lookups"