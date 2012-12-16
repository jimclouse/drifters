###
# Still exist on 2005-03-31
# existed 400 days prior
# on 2004-02-25 located > 0 N
select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' 
union select a.id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue  
into outfile '/tmp/drifters_pac_gyre5_2005.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n'
from gdpPacAll as a 
where day(a.obsDate) = 15 and a.obsTime = '12:00:00'
and id in (41487, 41485, 41499, 41167, 41476, 2602895, 27464, 36003);