#!/bin/bash
#
# This script should be run via curl:
#   bash -c "$(curl -kfsSL https://analyticsgit.riversidehealthcare.net/extract-management/extract-management-site/-/raw/master/publish/install.sh)"
#
# or via wget:
#   bash -c "$(wget -O- https://analyticsgit.riversidehealthcare.net/extract-management/extract-management-site/-/raw/master/publish/install.sh)"
#
# A server DNS can be specified by adding "DNS=something" before commands.
# A different sql remote can be specified.
#

# get custom dns

SITE=atlas
DNS=atlas.net
REMOTE=https://
ERROR=0

echo "$DNS"
#echo "$REMOTE"

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

fmt_green "Thanks for installing Atlas of Information Management!"


fmt_blue "Verifying required packages are installed"
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections

apt-get update -qq > /dev/null

command_install apt-utils
command_install pkg-config
command_install build-essential
command_install libssl-dev
command_install libffi-dev
command_install curl
command_install git
command_install wget
command_install libldap2-dev
command_install python3-dev
command_install python3-pip
command_install python3-setuptools
command_install unixodbc
command_install unixodbc-dev
command_install libpq-dev
command_install nginx
command_install sqlite3
command_install libsqlite3-0
command_install libsasl2-dev
command_install libxml2-dev
command_install libxmlsec1-dev
command_install redis-server
command_install ufw


fmt_blue "Updating timezone to CST"
sudo timedatectl set-timezone America/Chicago

fmt_blue "Setting up ufw port blocking"
sudo ufw default deny > /dev/null
sudo ufw allow ssh > /dev/null
sudo ufw allow "Nginx Full" > /dev/null
sudo ufw allow from 127.0.0.1 to any port 5001 > /dev/null
sudo ufw allow from 127.0.0.1 to any port 5002 > /dev/null
sudo ufw --force enable > /dev/null

# start redis
fmt_blue "Starting redis server"
$(which python3) -m pip install --disable-pip-version-check --quiet virtualenv setuptools wheel > /dev/null
sudo sed -i -e "s/supervised no/supervised systemd/g" /etc/redis/redis.conf > /dev/null
sudo systemctl enable redis-server > /dev/null
sudo systemctl start redis-server > /dev/null

# clear redis
# redis-cli FLUSHALL

# redis online?
fmt_green "Ping redis... $(redis-cli ping)?"

fmt_blue "Updating python settings"
export PYTHONDONTWRITEBYTECODE=1

fmt_blue "Installing SQL Server ODBC"
dpkg -s msodbcsql17 2>&1 |  grep -q 'is not installed' && fmt_install msodbcsql17 \
&& curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
&& curl -fsSL https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
&& sudo apt-get update --q \
&& sudo ACCEPT_EULA=Y apt-get install msodbcsql17 \
&& echo "export PATH=\"$PATH:/opt/mssql-tools/bin\"" >> ~/.bash_profile \
&& echo "export PATH=\"$PATH:/opt/mssql-tools/bin\"" >> ~/.bashrc \
&& echo "export PATH=\"$PATH:/opt/mssql-tools/bin\"" >> ~/.zshrc


HASHSCRIPT="
import hashlib
import time
print(hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()[:10])
"

HASH=$($(which python3) -c "$HASHSCRIPT")

fmt_green "Creating install directory /home/websites/$SITE/$HASH"
mkdir -p "/home/websites/$SITE/$HASH"
sudo chown -R webapp "/home/websites/$SITE/$HASH"

cd "/home/websites/$SITE/$HASH" || exit 1

sudo -u webapp git -c http.sslVerify=false clone --depth 1 "$REMOTE" . -q

fmt_green "${BOLD}Installing in /home/websites/$SITE/$HASH"

# create python environment
fmt_blue "Creating python environment"
sudo -u webapp virtualenv -q --clear --no-periodic-update venv


# install Extract Management 2.0
fmt_blue "Installing dependencies"

# install poetry - the package manager
# shellcheck disable=SC1091
# remove poetry config > it conflicts with install config.
rm poetry.toml && venv/bin/python -m pip install poetry --quiet
venv/bin/poetry config virtualenvs.in-project --unset
venv/bin/poetry config virtualenvs.create false --local
venv/bin/poetry install --no-dev --quiet
venv/bin/poetry add gunicorn --quiet
venv/bin/poetry add gevent --quiet

fmt_green "${UL}Env Info:"
fmt_yellow "$(venv/bin/poetry env info)"

# run migrations for celery
fmt_blue "Running Migrations:"
(cd atlas && ../venv/bin/poetry run python manage.py migrate django_celery_results)
(cd atlas && ../venv/bin/poetry run python manage.py migrate django_celery_beat)

# change ownership on sqlite db
sudo chown -R webapp "/home/websites/$SITE/$HASH/atlas/db.sqlite3"

# echo -e "\n${GREEN}Dep Info.${RESET}"
# echo -e "$(venv/bin/poetry show --tree)"

# make log files
fmt_blue "Creating gunicorn log files"
touch access.log && touch error.log
sudo chmod 777 access.log
sudo chmod 777 error.log


GUNICORN="atlas-py.$HASH.service"
fmt_blue "Updating gunicorn service file"
sed -i -e "s/hash/$HASH/g" publish/gunicorn.service

fmt_blue "Installing gunicorn service file"
sudo mv "publish/gunicorn.service" "/etc/systemd/system/$GUNICORN"

fmt_blue "Starting gunicorn service"
sudo systemctl start "$GUNICORN" && sudo systemctl enable "$GUNICORN" && sudo systemctl is-active "$GUNICORN" | grep "inactive" > /dev/null && sudo systemctl status "$GUNICORN" && ((ERROR++))


CELERY="atlas-py-celery.$HASH.service"
CELERY_BEAT="atlas-py-celery-beat.$HASH.service"

fmt_blue "Updating celery service file"
sed -i -e "s/hash/$HASH/g" publish/celery.service
sed -i -e "s/hash/$HASH/g" publish/celery_beat.service
sed -i -e "s/hash/$HASH/g" publish/celery.conf

fmt_blue "Installing celery service file"
sudo mv "publish/celery.service" "/etc/systemd/system/$CELERY"
sudo mv "publish/celery.conf" .
sudo mv "publish/celery_beat.service" "/etc/systemd/system/$CELERY_BEAT"

fmt_blue "Starting celery service"
sudo systemctl start "$CELERY" && sudo systemctl enable "$CELERY" && sudo systemctl is-active "$CELERY" | grep "inactive" > /dev/null && sudo systemctl status "$CELERY" && ((ERROR++))
sudo systemctl start "$CELERY_BEAT" && sudo systemctl enable "$CELERY_BEAT" && sudo systemctl is-active "$CELERY_BEAT" | grep "inactive" > /dev/null && sudo systemctl status "$CELERY_BEAT" && ((ERROR++))



# update nginx service files
fmt_blue "Updating hash in nginx service file"
if [ "$DNS" = none ]; then
  sed -i -e "s/80/80 default_server/g" publish/nginx
else
  sed -i -e "s/dns/$DNS/g" publish/nginx
fi
sed -i -e "s/hash/$HASH/g" publish/nginx

fmt_blue "Installing nginx service file"
mv publish/nginx /etc/nginx/sites-available/atlas-py

fmt_blue "Starting nginx service file"
ln -s /etc/nginx/sites-available/atlas-py /etc/nginx/sites-enabled &> install.log

fmt_green "Reloading Nginx!"
sudo systemctl reload nginx
sudo systemctl is-active nginx | grep "inactive" > install.log && echo "${RED}!!!Failed to reload Nginx!!!${RESET}" && ((ERROR++))

# remove old gunicorn processes
fmt_blue "Removing old gunicorn processes"
sudo systemctl reset-failed
(cd /etc/systemd/system/ && ls atlas-py*) | grep '^atlas-py' | grep -v "atlas-py.*$HASH" | xargs -i sh -c 'sudo systemctl disable {} || true && sudo systemctl stop {} || true && sudo rm -f /etc/systemd/system/{}'
sudo systemctl reset-failed

# remove old celery processes
fmt_blue "Removing old celery processes"
sudo systemctl reset-failed
(cd /etc/systemd/system/ && ls atlas-py-celery*) | grep '^atlas-py-celery' | grep -v "atlas-py-celery.*$HASH" | xargs -i sh -c 'sudo systemctl disable {} || true && sudo systemctl stop {} || true && sudo rm -f /etc/systemd/system/{}'
(cd /etc/systemd/system/ && ls atlas-py-celery-beat*) | grep '^atlas-py-celery-beat' | grep -v "atlas-py-celery-beat.*$HASH" | xargs -i sh -c 'sudo systemctl disable {} || true && sudo systemctl stop {} || true && sudo rm -f /etc/systemd/system/{}'
sudo systemctl reset-failed


# remove old instances of the website
fmt_blue "Removing old website instances"
(cd "/home/websites/$SITE/" && ls) | grep -v "$HASH" | xargs -i sh -c "sudo rm -rf /home/websites/$SITE/{} &>install.log"

# verify status
if [ "$DNS" = none ]; then
  DNS=localhost
fi

fmt_green "Checking online status - https://$DNS"

fmt_yellow "$(curl -sS "https://$DNS" --insecure -I)"

TITLE=$(curl -sS "https://$DNS" --insecure -so - | grep -iPo "(?<=<title>)(.*)(?=</title>)")
if [[ $TITLE == "Home - Atlas of Information Management" ]];
then
    fmt_green "Login page successfully reached!"
else
    fmt_error "Failed to reach login page! (Reached: $TITLE)"
    ((ERROR++))
fi;

fmt_blue "${UL}Debug Information"
echo -e "
${BLUE}${UL}Nginx${RESET}
${RED}sudo${RESET} tail -F /var/log/nginx/error.log
${RED}sudo${RESET} systemctl status ${GREEN}nginx${RESET}

${BLUE}${UL}Gunicorn and Celery${RESET}
${RED}sudo${RESET} journalctl -xe${RESET}

# check service status
${RED}sudo${RESET} systemctl status ${GREEN}$GUNICORN${RESET}
${RED}sudo${RESET} systemctl status ${GREEN}$CELERY${RESET}
${RED}sudo${RESET} systemctl status ${GREEN}$CELERY_BEAT${RESET}

# read error logs
${RED}tail -300${RESET} /home/websites/$SITE/${GREEN}$HASH${RESET}/error.log${RESET}

# reload gunicorn processes
${RED}sudo${RESET} systemctl daemon-reload

${YELLOW}Finally, don't forget to login and reschedule tasks!${RESET}
"

# return error if there was an error
exit "$ERROR"
