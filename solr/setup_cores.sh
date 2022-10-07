/opt/solr/bin/solr create -c atlas
#/opt/solr/bin/solr -c atlas -p 8983 -action set-user-property -property update.autoCreateFields -value false; \

/opt/solr/bin/solr create -c atlas_lookups
#/opt/solr/bin/solr -c atlas_lookups -p 8983 -action set-user-property -property update.autoCreateFields -value false; \

cp /var/solr/mine/solr-9.0.0/server/solr/atlas/conf/managed-schema /var/solr/data/atlas/conf/managed-schema
cp /var/solr/mine/solr-9.0.0/server/solr/atlas/conf/solrconfig.xml /var/solr/data/atlas/conf/solrconfig.xml
cp /var/solr/mine/solr-9.0.0/server/solr/atlas/conf/synonyms.txt /var/solr/data/atlas/conf/synonyms.txt
cp /var/solr/mine/solr-9.0.0/server/solr/atlas/conf/splitchars.txt /var/solr/data/atlas/conf/splitchars.txt
cp /var/solr/mine/solr-9.0.0/server/solr/atlas/conf/protwords.txt /var/solr/data/atlas/conf/protwords.txt
cp /var/solr/mine/solr-9.0.0/server/solr/atlas/conf/stopwords.txt /var/solr/data/atlas/conf/stopwords.txt
cp /var/solr/mine/solr-9.0.0/server/solr/atlas/conf/lang/stopwords_en.txt /var/solr/data/atlas/conf/lang/stopwords_en.txt

curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=atlas"

cp /var/solr/mine/solr-9.0.0/server/solr/atlas_lookups/conf/managed-schema /var/solr/data/atlas_lookups/conf/managed-schema
cp /var/solr/mine/solr-9.0.0/server/solr/atlas_lookups/conf/solrconfig.xml /var/solr/data/atlas_lookups/conf/solrconfig.xml
cp /var/solr/mine/solr-9.0.0/server/solr/atlas_lookups/conf/synonyms.txt /var/solr/data/atlas_lookups/conf/synonyms.txt
cp /var/solr/mine/solr-9.0.0/server/solr/atlas_lookups/conf/lang/stopwords_en.txt /var/solr/data/atlas_lookups/conf/lang/stopwords_en.txt
cp /var/solr/mine/solr-9.0.0/server/solr/atlas_lookups/conf/protwords.txt /var/solr/data/atlas_lookups/conf/protwords.txt
cp /var/solr/mine/solr-9.0.0/server/solr/atlas_lookups/conf/stopwords.txt /var/solr/data/atlas_lookups/conf/stopwords.txt

curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=atlas_lookups"
