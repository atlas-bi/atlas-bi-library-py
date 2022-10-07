# Running Solr for Dev/Testing


```sh
cd /to/this/solr/folder :)
# copy and paste to create.
docker run -d -v "$PWD:/var/solr/mine" -p 8983:8983 --name solr_dev solr:9 ""\
docker exec -it solr_dev bash -c "source /var/solr/mine/setup_cores.sh;" \
docker container restart solr_dev

# bash in and check things out
docker exec -it solr_dev bash  


# then to stop it
docker container stop solr_dev

# to run if already created
docker container start solr_dev

# and if you wanna delete it
docker container rm solr_dev

# or compiled:
docker container stop solr_dev; \
docker container rm solr_dev; \
docker run -d -v "$PWD:/var/solr/mine" -p 8983:8983 --name solr_dev solr:8; \
docker exec -it solr_dev bash -c "source /var/solr/mine/setup_cores.sh;" \
docker container restart solr_dev
```

Once running the admin dashboard can be accessed from [http://localhost:8983/solr/#/](http://localhost:8983/solr/#/).
