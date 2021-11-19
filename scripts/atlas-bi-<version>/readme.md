
# Ubuntu Build


```sh
apt-get update
apt-get install dh-make devscripts

rename atlas-bi-<version>
cd atlas-bi-<version>

debuild -us -uc

copy files to ppa repo
```

## To run in local docker
```sh
docker run --rm -it -v $(PWD):/atlas ubuntu:latest /bin/bash

cd /atlas; \
VERSION=0.0.1-rc.1; \
apt-get remove atlas-bi -y 2>/dev/null; \
rm -r "atlas-bi-$VERSION" 2>/dev/null; \
cp -r "atlas-bi-<version>" "atlas-bi-$VERSION" \
&& cd "atlas-bi-$VERSION" \
&& find . -type f -name "*" -exec sed -i'' -e "s/<version>/$VERSION/g" {} + \
&& debuild -us -uc --no-tgz-check \
&& cd .. \
&& apt-get install ./atlas-bi_*.deb -y


```