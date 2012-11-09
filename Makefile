SHELL=/bin/bash
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=ocean
GDP_START_YEAR=1990
GDP_END_YEAR=2011

DATA_PATH=/home/vagrant/ocean/data/


GDP_YEARTABLE_DEF = (id int\
					,obsDate datetime\
					,latitude float\
					,longitude float\
					,sst float\
					,ewct float\
					,nsct float\
					,latError float\
					,longError float\
					,origExpNum int\
					,wmoPlatform int\
					,hasDrogue boolean);

GDP_MERGETABLE_DROP = drop table if exists gdpAll;
GDP_MERGEDTABLE_DEF = create table if not exists gdpAll\
					(id int\
					,obsDateTime datetime\
					,obsDate date\
					,obsTime time\
					,latitude float\
					,longitude float\
					,longitudeWest float\
					,sst float\
					,ewct float\
					,nsct float\
					,latError float\
					,longError float\
					,origExpNum int\
					,wmoPlatform int\
					,hasDrogue boolean);

GDP_MERGETABLE_INDEX = alter table gdpAll add index(id, obsDate, obsTime);\
					   alter table gdpAll add index(obsDate, obsTime);\
					   alter table gdpAll add index(obsTime, obsDate);

GDP_INSERT = insert into gdpAll (id\
					,obsDateTime\
					,obsDate\
					,obsTime\
					,latitude\
					,longitude\
					,longitudeWest\
					,sst\
					,ewct\
					,nsct\
					,latError\
					,longError\
					,origExpNum\
					,wmoPlatform\
					,hasDrogue)\
	select 			id\
					,obsDate\
					,date(obsDate) as obsDate\
					,time(obsDate) as obsTime\
					,latitude\
					,longitude\
					,-1.0 * longitude as longitudeWest\
					,sst\
					,ewct\
					,nsct\
					,latError\
					,longError\
					,origExpNum\
					,wmoPlatform\
					,hasDrogue\
	from 			gdp$$number\
	order by 		id\
					,obsDate;


GDP_ALT_TABLE_DEF = (id int, wmo int, expno int, typebuoy varchar(30), ddate date, dtime time, dlat float, dlon float, edate date, etime time, elat float, elon float, ldate date, ltime time, typedeath varchar(64) );

default:
	sudo apt-get update;
	sudo apt-get -y install dos2unix;
	sudo apt-get -y install mysql-server python2.7-dev python-pip;
	sudo apt-get -y build-dep python-mysqldb;

	$(MAKE) install_python


setup_mysql:
	create database ocean character set utf8 collate utf8_general_ci;

install_python:
	easy_install -U distribute;
	pip install PyYAML;
	pip install MySQL-python;

# gdp (global drifter program) data contains drifter data sets from 1990-2012 over all the world's oceans
# this project looks at north atlantic drifters only
load_gdp:
	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdp$$number $(GDP_YEARTABLE_DEF)"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "truncate table gdp$$number;"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH)gdp$$number.csv' into table gdp$$number fields terminated by ',' ;"; \
		((number = number + 1)) ; \
	done

load_gdp_alt:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdpAlt $(GDP_ALT_TABLE_DEF)"; \
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "truncate table gdpAlt;"; \
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH)gdpAlt.csv' into table gdpAlt fields terminated by ',' ;"; \

single_view_gdp:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_MERGETABLE_DROP)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_MERGEDTABLE_DEF)";

	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_INSERT)"; \
		((number = number + 1)) ; \
	done
	$(MAKE) gdp_all_index
	
gdp_all_index:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_MERGETABLE_INDEX)";

