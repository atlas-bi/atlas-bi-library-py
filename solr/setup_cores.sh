/opt/solr/bin/solr create -c atlas
#/opt/solr/bin/solr -c atlas -p 8983 -action set-user-property -property update.autoCreateFields -value false; \

/opt/solr/bin/solr create -c atlas_lookups
#/opt/solr/bin/solr -c atlas_lookups -p 8983 -action set-user-property -property update.autoCreateFields -value false; \

cp /var/solr/mine/atlas/managed-schema /var/solr/data/atlas/conf/managed-schema
cp /var/solr/mine/atlas/solrconfig.xml /var/solr/data/atlas/conf/solrconfig.xml
cp /var/solr/mine/atlas/synonyms.txt /var/solr/data/atlas/conf/synonyms.txt
cp /var/solr/mine/atlas/splitchars.txt /var/solr/data/atlas/conf/splitchars.txt
cp /var/solr/mine/atlas/protwords.txt /var/solr/data/atlas/conf/protwords.txt
cp /var/solr/mine/atlas/stopwords.txt /var/solr/data/atlas/conf/stopwords.txt
cp /var/solr/mine/atlas/lang/stopwords_en.txt /var/solr/data/atlas/conf/lang/stopwords_en.txt

curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=atlas"

cp /var/solr/mine/atlas_lookups/managed-schema /var/solr/data/atlas_lookups/conf/managed-schema
cp /var/solr/mine/atlas_lookups/solrconfig.xml /var/solr/data/atlas_lookups/conf/solrconfig.xml
cp /var/solr/mine/atlas_lookups/synonyms.txt /var/solr/data/atlas_lookups/conf/synonyms.txt
cp /var/solr/mine/atlas_lookups/lang/stopwords_en.txt /var/solr/data/atlas_lookups/conf/lang/stopwords_en.txt
cp /var/solr/mine/atlas_lookups/protwords.txt /var/solr/data/atlas_lookups/conf/protwords.txt
cp /var/solr/mine/atlas_lookups/stopwords.txt /var/solr/data/atlas_lookups/conf/stopwords.txt

curl "http://localhost:8983/solr/admin/cores?action=RELOAD&core=atlas_lookups"
