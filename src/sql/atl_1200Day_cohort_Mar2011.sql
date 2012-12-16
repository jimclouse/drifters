### Atlantic drifters
# Still exist on 2007-03-31
# existed 800 days prior
# on 2005-01-21 located > 0 N
select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' 
union select a.id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue  
into outfile '/tmp/drifters_atl_1200_end_2011.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n'
from gdpAtlAll as a 
join (      select g.id from (select distinct id from gdpAtlAll) as g
            where exists ( select 1 from gdpAtlAll s2 where s2.id = g.id and s2.obsDate = '2011-03-31') 
               and exists ( select 1 from gdpAtlAll s3 where s3.id = g.id and s3.obsDate = '2007-12-17' and s3.latitude > 0 )
) as sub
on a.id = sub.id
where day(a.obsDate) = 15 and a.obsTime = '12:00:00';
