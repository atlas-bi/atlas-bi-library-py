# this script is to work with the ubuntu installer

apt-get update
apt-get install atlas-bi
apt-get install ufw redis

fmt_blue "Setting up ufw port blocking"
ufw default deny > /dev/null
ufw allow ssh > /dev/null
ufw allow "Nginx Full" > /dev/null
ufw --force enable > /dev/null



sed -i -e "s/supervised no/supervised systemd/g" /etc/redis/redis.conf > /dev/null
systemctl enable redis-server > /dev/null
systemctl start redis-server > /dev/null


fmt_blue "Installing SQL Server ODBC"
dpkg -s msodbcsql17 2>&1 |  grep -q 'is not installed' && fmt_install msodbcsql17 \
&& curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
&& curl -fsSL https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
&& apt-get update --q \
&& ACCEPT_EULA=Y apt-get install msodbcsql17 \
&& echo "export PATH=\"$PATH:/opt/mssql-tools/bin\"" >> ~/.bash_profile \
&& echo "export PATH=\"$PATH:/opt/mssql-tools/bin\"" >> ~/.bashrc \
&& echo "export PATH=\"$PATH:/opt/mssql-tools/bin\"" >> ~/.zshrc