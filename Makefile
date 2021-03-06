#
SHELL=/bin/bash
HOME=$(shell pwd)
SQL_TEMPLATES=$(HOME)/sql/templates
DATA_PATH=$(HOME)/data/drifters/
DATA_PATH_ATL=$(DATA_PATH)Atlantic/
DATA_PATH_PAC=$(DATA_PATH)Pacific/

MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=ocean

GDP_START_YEAR=2000
GDP_END_YEAR=2012

GDP_ATL_MERGETABLE_DROP = drop table if exists gdpAll;
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

GDP_ATL_MERGETABLE_INDEX = alter table gdpAll add index(id, obsDate, obsTime);\
					   alter table gdpAll add index(obsDate, obsTime);\
					   alter table gdpAll add index(obsTime, obsDate);

GDP_PAC_MERGETABLE_INDEX = alter table gdpPacAll add index(id, obsDate, obsTime);\
					   alter table gdpPacAll add index(obsDate, obsTime);\
					   alter table gdpPacAll add index(obsTime, obsDate);

# load sql templates from file
gdp_adjusted=`cat $(SQL_TEMPLATES)/gdp_adjusted.sql.tpl`
gdp_yearable=`cat $(SQL_TEMPLATES)/gdp_yeartable.sql.tpl`
fisherResultsTable=`cat $(SQL_TEMPLATES)/fisherResults.sql.tpl`
fn_significance=`cat $(SQL_TEMPLATES)/fn_significance.sql.tpl`
chiSquareResults=`cat $(SQL_TEMPLATES)/chiSquareResults.sql.tpl`
chiResiduals=`cat $(SQL_TEMPLATES)/chiResiduals.sql.tpl`
percentages=`cat $(SQL_TEMPLATES)/percentages.sql.tpl`
GDP_INSERT=`cat $(SQL_TEMPLATES)/gdp_insert.sql.tpl`


default:
	sudo apt-get update;
	sudo apt-get -y install dos2unix;
	sudo apt-get -y install mysql-server python2.7-dev python-pip;
	sudo apt-get -y build-dep python-mysqldb;
	sudo apt-get -y install python-numpy python-scipy r-base;

	$(MAKE) install_python

lifespan:
	cd src; python lifespan.py

reassign:
	cd src; python reAssign.py

identify_convergence:
	cd src; python identifyConvergence.py

export_cohorts:
	cd src; python exportCohorts.py

analyze_env_data:
	cd src; python envDataAnalysis.py

interval_data:
	cd src; python prepareIntervalData.py

setup_mysql:
	create database ocean character set utf8 collate utf8_general_ci;

install_python:
	easy_install -U distribute;
	pip install PyYAML;
	pip install MySQL-python;
	pip install rpy2

# gdp (global drifter program) data contains drifter data sets from 1990-2012 over all the world's oceans
# this project looks at north atlantic drifters only
load_gdp:
	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdp$$number $(gdp_yearable)"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "truncate table gdp$$number;"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH_ATL)gdp$$number.csv' into table gdp$$number fields terminated by ',' ;"; \
		((number = number + 1)) ; \
	done

load_gdp_pac:
	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdpPac$$number $(gdp_yearable)"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "truncate table gdpPac$$number;"; \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH_PAC)gdpPac$$number.csv' into table gdpPac$$number fields terminated by ',' ;"; \
		((number = number + 1)) ; \
	done

load_gdp_pac_adj:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdpPacAdj $(gdp_adjusted)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "truncate table gdpPacAdj;";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH_PAC)gdpPacAll_adjusted.txt' into table gdpPacAdj fields terminated by ',' ;";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "alter table gdpPacAdj add index(obsDate, id); alter table gdpPacAdj add index(id, obsDate);";

load_gdp_atl_adj:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdpAtlAdj $(gdp_adjusted)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "truncate table gdpAtlAdj;";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "load data local infile '$(DATA_PATH_ATL)gdpAtlAll_adjusted.csv' into table gdpAtlAdj fields terminated by ',' ;";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "alter table gdpAtlAdj add index(obsDate, id); alter table gdpAtlAdj add index(id, obsDate);";


single_view_gdp_atl:
	# because mysql doesnt support materialized views, need to create a real table to add sufficient indexes
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_MERGETABLE_DROP)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_MERGEDTABLE_DEF)";

	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "insert into gdpAtlAll $(GDP_INSERT)"; \
		((number = number + 1)) ; \
	done
	$(MAKE) gdp_AtlAll_index

single_view_gdp_pac:
	# because mysql doesnt support materialized views, need to create a real table to add sufficient indexes
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_PAC_MERGETABLE_DROP)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "create table if not exists gdpPacAll $(GDP_MERGEDTABLE_DEF)";

	number=$(GDP_START_YEAR) ; while [[ $$number -le $(GDP_END_YEAR) ]] ; do \
		mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "insert into gdpPacAll $(GDP_INSERT)"; \
		((number = number + 1)) ; \
	done
	$(MAKE) gdp_pacAll_index

setup_results_tables:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(fisherResultsTable)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(fn_significance)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(chiSquareResults)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(chiResiduals)";
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(percentages)";

gdp_pacAll_index:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_PAC_MERGETABLE_INDEX)";

gdp_AtlAll_index:
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "$(GDP_ATL_MERGETABLE_INDEX)";

export_gdpPac:
	#mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' union select id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue into outfile '/tmp/gdpPac_2006.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' from gdpPacAll where obsDate >= '2006-01-01' and obsDate < '2006-06-01' and latitude > 0 and longitudeWest < -135;"
	mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' union select id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue into outfile '/tmp/gdpPac_2006_04-01.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' from gdpPacAll g where exists ( select 1 from gdpPacAll s1 where s1.id = g.id and     s1.obsDate = '2006-03-19' and     s1.latitude >= 30.0 and     s1.latitude <= 45.0 and     s1.longitudeWest > -180.0 and     s1.longitudeWest < -150.0) and exists ( select 1 from gdpPacAll s2 where s2.id = g.id and     s2.obsDate = '2006-04-01' ) and exists ( select 1 from gdpPacAll s3 where s3.id = g.id and     s3.obsDate = '2006-02-19');"
	#mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' union select id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue into outfile '/tmp/gdp_2010.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' from gdpAll where obsDate >= '2009-12-01' and obsDate < '2010-07-01' and latitude > 0;"
	#mysql --user=$(MYSQL_USER) --password=$(MYSQL_PASSWORD) $(MYSQL_DATABASE) -v -v --show_warnings -e "select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' union select id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue into outfile '/tmp/gdp_2011.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' from gdpAll where obsDate >= '2010-12-01' and obsDate < '2011-07-01' and latitude > 0;"
