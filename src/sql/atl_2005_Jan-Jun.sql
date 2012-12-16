select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' 
union select a.id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue  
into outfile '/tmp/drifters_atl_2005.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n'
from gdpAll as a 
join (      select g.id from (select distinct id from gdpAll) as g
            where exists ( 
                select 1 from gdpAll s1 where s1.id = g.id 
                    and     s1.latitude >= 0.0 
                    and s1.latitude <= 60.0 and     s1.longitudeWest < -10.0
                    and s1.longitudeWest > -90.0
                    and ( s1.obsDate >= '2005-01-01' and s1.obsDate <= '2005-06-01'))
               and exists ( select 1 from gdpAll s2 where s2.id = g.id and s2.obsDate = '2005-06-01') 
               and exists ( select 1 from gdpAll s3 where s3.id = g.id and s3.obsDate = '2004-12-01')
) as sub
on a.id = sub.id
where a.obsDate >= '2005-01-01' and a.obsDate <= '2005-06-01';