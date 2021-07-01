# Running Solr for Testing


To run solr for testing with docker

```sh
cd /to/this/solr/folder :)
# copy and paste to create.
docker run -d -v "$PWD:/var/solr/mine" -p 8983:8983 --name solr_dev solr:8 bash -c ""\
docker exec -it solr_dev bash source /var/solr/mine/setup_cores.sh; \
docker container restart solr_dev

# bash in and check things out
docker exec -it solr_dev bash  


# then to stop it
docker container stop solr_dev

# to run if already created
docker container start solr_dev

# and if you wanna delete it
docker container rm solr_dev

```
docker container stop solr_dev; \
docker container rm solr_dev; \
docker run -d -v "$PWD:/var/solr/mine" -p 8983:8983 --name solr_dev solr:8; \
docker exec -it solr_dev bash -c "source /var/solr/mine/setup_cores.sh;" \
docker container restart solr_dev