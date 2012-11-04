SHELL=/bin/bash
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=ocean
GDP_START_YEAR=1990
GDP_END_YEAR=2011

DATA_PATH=/home/vagrant/ocean/data/

default:
	sudo apt-get update;
	sudo apt-get -y install dos2unix;
	sudo apt-get -y install mysql-server;


setup_mysql:
	create database ocean character set utf8 collate utf8_general_ci;

# gdp (global drifter program) data contains drifter data sets from 1990-2012 over all the world's oceans
# this project looks at north atlantic drifters only
load_gdp:
	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdp$$number (id int,obsDate datetime,latitude float,longitude float,sst float,ewct float,nsct float,latError float,longError float,origExpNum int,wmoPlatform int,hasDrogue boolean);"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "truncate table gdp$$number;"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH)gdp$$number.csv' into table gdp$$number fields terminated by ',' ;"; \
		((number = number + 1)) ; \
	done