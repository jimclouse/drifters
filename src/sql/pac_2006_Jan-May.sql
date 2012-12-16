select 'id', 'obsDateTime', 'obsDate', 'obstime', 'latitude', 'longitude', 'longitudeWest', 'sst', 'hasDrogue' 
union select a.id, obsDateTime, obsDate, obstime, latitude, longitude, longitudeWest, sst, hasDrogue  
into outfile '/tmp/jim1_2006.csv' FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n'
from gdpPacAll as a 
join (      select g.id from (select distinct id from gdpPacAll) as g
            where exists ( 
                select 1 from gdpPacAll s1 where s1.id = g.id 
                    and     s1.latitude >= 30.0 
                    and s1.latitude <= 45.0 and     s1.longitudeWest > -180.0
                    and s1.longitudeWest < -150.0
                    and ( s1.obsDate >= '2006-01-01' and s1.obsDate <= '2006-05-01'))
               and exists ( select 1 from gdpPacAll s2 where s2.id = g.id and s2.obsDate = '2006-05-01') 
               and exists ( select 1 from gdpPacAll s3 where s3.id = g.id and s3.obsDate = '2005-12-01')
) as sub
on a.id = sub.id
where a.obsDate >= '2006-01-01' and a.obsDate <= '2006-05-01';