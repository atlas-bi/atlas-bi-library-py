#!/bin/sh

# recommeneded to have ufw installed
#
# ufw default deny > /dev/null
# ufw allow ssh > /dev/null
# ufw allow "Nginx Full" > /dev/null
# ufw --force enable > /dev/null


# Ideally there will be a user config file "/etc/atlas-bi/config". This file will hold
# the database connection, colors and any other user settings.

# If a db has not been added to the file, atlas will show a configuration screen.

# configuration screen is available if there is no db, or a user is superuser.

# After changing the configuration, the app will "reconfigure" - run npm install, db migrate etc.


VERSION=<version>

color() {
  RED=$(printf '\033[31m')
  GREEN=$(printf '\033[32m')
  YELLOW=$(printf '\033[33m')
  BLUE=$(printf '\033[34m')
  UL=$(printf '\033[4m')
  BOLD=$(printf '\033[1m')
  RESET=$(printf '\033[0m') # No Color
}

fmt_error() {
  echo "${RED}Error: $1${RESET}" >&2
}

fmt_install() {
  echo "${YELLOW}Installing: $1${RESET}"
}

fmt_blue() {
  echo "${BLUE}$1${RESET}"
}

fmt_green() {
  echo "${GREEN}$1${RESET}"
}

fmt_yellow() {
  echo "${YELLOW}$1${RESET}"
}

command_install() {
  dpkg -s "$@" 2>&1 |  grep -q 'is not installed' && fmt_install "$@" && apt-get install -q -qq "$@" > /dev/null
}

color

cd /usr/bin/atlas-bi/

echo "${YELLOW}"
echo "

         .8.    8888888 8888888888 8 8888                  .8.            d888888o.
        .888.         8 8888       8 8888                 .888.         ..8888:' .88.
       :88888.        8 8888       8 8888                :88888.        8..8888.   Y8
      . :88888.       8 8888       8 8888               . .88888.       .8..8888.
     .8. .88888.      8 8888       8 8888              .8. .88888.       .8..8888.
    .8.8. .88888.     8 8888       8 8888             .8.8. .88888.       .8..8888.
   .8' .8. .88888.    8 8888       8 8888            .8' .8. .88888.       .8..8888.
  .8'   .8. .88888.   8 8888       8 8888           .8'   .8. .88888.  8b   .8..8888.
 .888888888. .88888.  8 8888       8 8888          .888888888. .88888. .8b.  ;8..8888
.8'       .8. .88888. 8 8888       8 888888888888 .8'       .8. .88888. .Y8888P ,88P'

"

fmt_green "Thanks for installing Atlas BI Library!"

wget -q --show-progress -O- "https://github.com/atlas-bi/atlas-bi-library-py/archive/refs/tags/$VERSION.tar.gz" | tar -xz -C .

cd "atlas-bi-library-py-$VERSION"

# static should be pre-built in release and not need this command.
fmt_blue "Building static"
npm install
npm run build


# fmt_blue "Updating python settings"
# virtualenv required by Poetry
# $(which python3) -m pip install --disable-pip-version-check --quiet virtualenv > /dev/null

fmt_blue "Installing Poetry"
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | $(which python3) -

# remove poetry config > it conflicts with install config.
"$HOME/.local/bin/poetry" config --local virtualenvs.in-project true
"$HOME/.local/bin/poetry" config --local virtualenvs.create true
"$HOME/.local/bin/poetry" install --no-dev

fmt_blue "Updating nginx"

touch nginx.log
touch nginx_error.log

rm /etc/nginx/sites-enabled/atlas_bi 2> /dev/null
ln -s publish/nginx /etc/nginx/sites-enabled/atlas_bi


fmt_blue "Installing Apache Solr"
# install Apache Solr
wget https://archive.apache.org/dist/lucene/solr/8.9.0/solr-8.9.0.tgz
tar xzf solr-8.9.0.tgz
solr-8.9.0/bin/install_solr_service.sh solr-8.9.0.tgz


fmt_blue "Setting Up Database"
su - postgres -c "/etc/init.d/postgresql start && psql --command \"CREATE USER atlas_me WITH SUPERUSER PASSWORD 'nothing';\"  && createdb -O atlas_me atlas_db"

# not a docker image.. has systemd installed and running
if [ "$(pidof systemd)" != "" ]; then
    fmt_green "Using systemd as service runner."

    fmt_green "Reloading Nginx!"

    systemctl reload nginx
    systemctl is-active nginx | grep "inactive" && echo "${RED}!!!Failed to reload Nginx!!!${RESET}" && (exit 1)

    fmt_green "Starting Atlas!"
    systemctl enable atlas_bi_celery.service
    systemctl enable atlas_bi_celery_beat.service
    systemctl enable atlas_bi_gunicorn.service

    fmt_green "Starting Solr!"
    systemctl enable solr
else
    # use supervisord
    # supervisord should have
    # - nginx
    # - gunicorn
    # - celery
    # - celerybeat
    # - redis
    fmt_blue "Using supervisor as service runner"
    "$HOME/.local/bin/poetry" add --lock supervisor
    "$HOME/.local/bin/poetry" install --no-dev
    pkill -f supervisord
    "$HOME/.local/bin/poetry" run supervisord -c ../atlas_bi_supervisord.conf -d "/usr/bin/atlas-bi/atlas-bi-library-py-$VERSION"
fi

