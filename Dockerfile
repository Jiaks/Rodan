# Base version
FROM	ubuntu:14.04

# Use bash. For virtualenv.
RUN	rm /bin/sh && ln -s /bin/bash /bin/sh

# Update system.
RUN	apt-get -y update && apt-get -y upgrade


# Set up Rodan core

## Prerequisites
RUN	apt-get -y install python2.7 git-core python-pip wget autoconf

## Get Rodan source
RUN	mkdir -p /srv/webapps
WORKDIR	"/srv/webapps"
RUN	git clone --recursive https://github.com/DDMAL/Rodan.git
WORKDIR	"/srv/webapps/Rodan"
RUN	git checkout develop

## Install RabbitMQ: http://www.rabbitmq.com/install-debian.html
RUN	echo "# RabbitMQ" >> /etc/apt/sources.list
RUN	echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list

RUN	cd /tmp && wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
RUN	apt-key add /tmp/rabbitmq-signing-key-public.asc
RUN	apt-get -y update
RUN	apt-get -y install rabbitmq-server


## Create Python virtual environment
RUN	pip install virtualenv
RUN	virtualenv --no-site-packages rodan_env
RUN	source ./rodan_env/bin/activate

## Install Python packages
RUN	apt-get -y install libpython-dev lib32ncurses5-dev libxml2-dev libxslt1-dev zlib1g-dev lib32z1-dev
RUN     source ./rodan_env/bin/activate && pip install -r requirements.txt

## Install PostgreSQL [TODO: conditionally]
RUN	apt-get -y install postgresql postgresql-contrib libpq-dev
RUN	source ./rodan_env/bin/activate && pip install psycopg2

## Configure PostgreSQL
RUN	service postgresql start && sudo -u postgres psql --command "create user rodan with password 'tOX?&s+m]*F0_^r';" && sudo -u postgres psql --command 'create database rodan;' && sudo -u postgres psql --command 'grant all privileges on database "rodan" to rodan;'

## Set up Celery Queue [TODO: conditionally]
RUN	service rabbitmq-server start && rabbitmqctl add_user rodanuser DDMALrodan && rabbitmqctl add_vhost DDMAL && rabbitmqctl set_permissions -p DDMAL rodanuser ".*" ".*" ".*"


## Install Gamera
RUN     mkdir /src && chmod 755 /src
WORKDIR	"/src"
RUN     apt-get -y install libpng-dev libtiff-dev
RUN     wget "http://sourceforge.net/projects/gamera/files/gamera/gamera-3.4.2/gamera-3.4.2.tar.gz/download" -O gamera-3.4.2.tar.gz && tar xvf gamera-3.4.2.tar.gz && source /srv/webapps/Rodan/rodan_env/bin/activate && cd gamera-3.4.2 && python setup.py install --nowx
RUN     wget http://gamera.informatik.hsnr.de/addons/musicstaves/musicstaves-1.3.10.tar.gz && tar xvf musicstaves-1.3.10.tar.gz && source /srv/webapps/Rodan/rodan_env/bin/activate && cd musicstaves-1.3.10 && CFLAGS="-I/src/gamera-3.4.2/include" python setup.py install
RUN     git clone https://github.com/DDMAL/document-preprocessing-toolkit.git && cd document-preprocessing-toolkit && source /srv/webapps/Rodan/rodan_env/bin/activate && export CFLAGS="-I/src/gamera-3.4.2/include" && cd background-estimation && python setup.py install && cd ../border-removal && python setup.py install && cd ../staffline-removal && python setup.py install && cd ../lyric-extraction && python setup.py install

## Install LibMEI

RUN     git clone https://github.com/DDMAL/libmei.git && cd libmei/tools && pip install lxml && python parseschema2.py -o src -l cpp /srv/webapps/Rodan/helper_scripts/neumes_and_layout_compiled.xml && python parseschema2.py -o src -l python /srv/webapps/Rodan/helper_scripts/neumes_and_layout_compiled.xml && rm -rf ../src/modules/* && rm -rf ../python/pymei/Modules/* && mv src/cpp/* ../src/modules/ && mv src/python/* ../python/pymei/Modules/ && apt-get -y install uuid-dev libxml2-dev cmake && cd .. && mkdir build && cd build && cmake .. && make && make install
RUN     apt-get -y install build-essential python-dev python-setuptools libboost-python-dev libboost-thread-dev && cd libmei/python && wget https://gist.githubusercontent.com/lingxiaoyang/3e50398e9fef44b62206/raw/75706f28b9eef76635ca24be6d5f1b90fa5e40de/setup.py.patch && patch setup.py < setup.py.patch && source /srv/webapps/Rodan/rodan_env/bin/activate && python setup.py install

## xmllint
RUN     apt-get -y install libxml2-utils


# Graphics Magick
RUN     apt-get -y install graphicsmagick-imagemagick-compat

# Kakadu
COPY    v7_7-01273N.zip /src/
RUN     apt-get -y install unzip
RUN     unzip v7_7-01273N.zip
RUN     cd v7_7-01273N/coresys/make && make -f Makefile-Linux-x86-64-gcc
RUN     cd v7_7-01273N/apps/make && make -f Makefile-Linux-x86-64-gcc
RUN     cp v7_7-01273N/lib/Linux-x86-64-gcc/* /usr/local/lib && cp v7_7-01273N/bin/Linux-x86-64-gcc/* /usr/local/bin


## IIP Server
RUN     git clone https://github.com/ruven/iipsrv.git && apt-get -y install libmemcached-dev libtool && cd iipsrv && ./autogen.sh && ./configure --with-kakadu=/src/v7_7-01273N && make -j4 && mkdir /srv/fcgi-bin && cp src/iipsrv.fcgi /srv/fcgi-bin


## Configure Rodan
WORKDIR	"/srv/webapps/Rodan"
RUN     echo "trigger update" && git pull && git checkout autoconf
RUN     autoconf
RUN     mkdir /mnt/rodan_data
RUN     apt-get -y install libvips-tools
RUN     ./configure --enable-debug=no --enable-diva RODAN_VENV_DIR=/srv/webapps/Rodan/rodan_env/ RODAN_DATA_DIR=/mnt/rodan_data DB_PASSWORD="tOX?&s+m]*F0_^r" DOMAIN_NAME="192.168.59.103" IIPSRV_FCGI=/srv/fcgi-bin/iipsrv.fcgi
RUN	service postgresql start && source ./rodan_env/bin/activate && python manage.py makemigrations && python manage.py migrate
RUN     chmod a+x /srv/webapps/Rodan/celery_start.sh /srv/webapps/Rodan/gunicorn_start.sh

RUN     apt-get -y install nginx

## Set up permission
RUN     touch /srv/webapps/Rodan/rodan.log
RUN	chgrp -R www-data /srv/webapps/Rodan
RUN     chmod g+w /srv/webapps/Rodan/rodan.log
RUN     chown www-data:www-data /mnt/rodan_data


## Configure nginx [Conditionally]
RUN     rm /etc/nginx/sites-enabled/* && cp etc/nginx/sites-available/rodan_with_diva /etc/nginx/sites-available && ln -s /etc/nginx/sites-available/rodan_with_diva /etc/nginx/sites-enabled/rodan_with_diva


## Install supervisor
RUN	apt-get -y install supervisor

## Configure supervisor
RUN     cp etc/supervisor/conf.d/*.conf /etc/supervisor/conf.d/


## create super user for Rodan [TODO]
RUN     service postgresql start && source ./rodan_env/bin/activate && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell

## Start server!
EXPOSE  80
EXPOSE  5432
EXPOSE  5672
CMD     service rabbitmq-server start && service postgresql start && service nginx start && /usr/bin/supervisord -n
