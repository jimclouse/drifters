SHELL=/bin/bash
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=ocean
GDP_START_YEAR=2005
GDP_END_YEAR=2011

DATA_PATH=/home/vagrant/ocean/data/
DATA_PATH_PAC=$(DATA_PATH)drifters/Pacific/

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
GDP_PAC_MERGETABLE_DROP = drop table if exists gdpPacAll;
GDP_MERGEDTABLE_DEF = (id int\
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

GDP_PAC_MERGETABLE_INDEX = alter table gdpPacAll add index(id, obsDate, obsTime);\
					   alter table gdpPacAll add index(obsDate, obsTime);\
					   alter table gdpPacAll add index(obsTime, obsDate);

GDP_INSERT = (id\
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
	from 			gdpPac$$number\
	order by 		id\
					,obsDate;


GDP_ALT_TABLE_DEF = (id int, wmo int, expno int, typebuoy varchar(30), ddate date, dtime time, dlat float, dlon float, edate date, etime time, elat float, elon float, ldate date, ltime time, typedeath varchar(64) );

GTS_TABLE_DEF = (Identifier int, Odate date, OTime time, Lat float, Lon float, QC_POS smallint ,PDT varchar(12), PTM varchar(12), Drogue varchar(24), SST float, QC_SST varchar(10), Airtemp float, QC_AirT varchar(10), Pressure float, QC_Pr varchar(10), WSp float, QC_WS varchar(10), WDir float, QC_WD varchar(10), RelHum float, QC_RH varchar(10))

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
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH)gdpAlt.csv' into table gdpAlt fields terminated by ',';"; \

single_view_gdp:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_MERGETABLE_DROP)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_MERGEDTABLE_DEF)";

	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_INSERT)"; \
		((number = number + 1)) ; \
	done
	$(MAKE) gdp_all_index

load_gdp_pac:
	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdpPac$$number $(GDP_YEARTABLE_DEF)"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "truncate table gdpPac$$number;"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH_PAC)gdpPac$$number.csv' into table gdpPac$$number fields terminated by ',' ;"; \
		((number = number + 1)) ; \
	done

single_view_gdp_pac:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_PAC_MERGETABLE_DROP)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdpPacAll $(GDP_MERGEDTABLE_DEF)";

	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "insert into gdpPacAll $(GDP_INSERT)"; \
		((number = number + 1)) ; \
	done
	$(MAKE) gdp_pacAll_index

load_gts:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "drop table if exists gts"; \
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gts $(GTS_TABLE_DEF)"; \
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "truncate table gts;"; \
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH)gts.csv' into table gts fields terminated by ',' IGNORE 1 LINES;"; \
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "alter table gts add index(Identifier); alter table gts add index(Odate, OTime); update gts set Drogue = NULL where Drogue = '         ';"

export_gts:
	select o.Identifier, o.OTime, o.Lat, o.Lon, -1.0 * o.Lon as InvLong, o.Drogue from gts o join ( select Identifier, min(OTime) as OTime from gts where Odate = '2009-01-29' group by Identifier) i on o.Identifier = i.Identifier and o.OTime = i.OTime where o.Odate = '2009-01-29';
	
gdp_pacAll_index:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_PAC_MERGETABLE_INDEX)";

gdp_all_index:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_MERGETABLE_INDEX)";

export_gdpPac:
	#mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' union select id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue into outfile '/tmp/gdpPac_2006.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' from gdpPacAll where obsDate >= '2006-01-01' and obsDate < '2006-06-01' and latitude > 0 and longitudeWest < -135;"
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' union select id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue into outfile '/tmp/gdpPac_2006_04-01.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' from gdpPacAll g where exists ( select 1 from gdpPacAll s1 where s1.id = g.id and     s1.obsDate = '2006-03-19' and     s1.latitude >= 30.0 and     s1.latitude <= 45.0 and     s1.longitudeWest > -180.0 and     s1.longitudeWest < -150.0) and exists ( select 1 from gdpPacAll s2 where s2.id = g.id and     s2.obsDate = '2006-04-01' ) and exists ( select 1 from gdpPacAll s3 where s3.id = g.id and     s3.obsDate = '2006-02-19');"
	#mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' union select id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue into outfile '/tmp/gdp_2010.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' from gdpAll where obsDate >= '2009-12-01' and obsDate < '2010-07-01' and latitude > 0;"
	#mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' union select id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue into outfile '/tmp/gdp_2011.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' from gdpAll where obsDate >= '2010-12-01' and obsDate < '2011-07-01' and latitude > 0;"
