###
# Still exist on 2005-03-31
# existed 400 days prior
# on 2004-02-25 located > 0 N
select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' 
union select a.id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue  
into outfile '/tmp/drifters_pac_400_end_2005.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n'
from gdpPacAll as a 
join (      select g.id from (select distinct id from gdpPacAll) as g
            where exists ( select 1 from gdpPacAll s2 where s2.id = g.id and s2.obsDate = '2005-03-31') 
               and exists ( select 1 from gdpPacAll s3 where s3.id = g.id and s3.obsDate = '2004-02-25' and s3.latitude > 0 )
) as sub
on a.id = sub.id
where day(a.obsDate) = 15 and a.obsTime = '12:00:00';