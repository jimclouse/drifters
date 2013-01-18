drop table if exists gdpPacDeployment;
create table gdpPacDeployment (id int, latitude float, longitude float, deployDate date, index(id), index(deployDate));
insert into gdpPacDeployment (id, latitude, longitude, deployDate)
select g2.id
        ,g2.latitude
        ,g2.longitude
        ,g2.obsDate
from (
select g1.id, g1.obsDate, max(g1.obsTime) as obsTime
from (select id, min(obsDate) as obsDate from gdpPacAll group by id) as i1 join gdpPacAll g1 
on g1.id = i1.id and g1.obsDate = i1.obsDate
group by g1.id, g1.obsDate ) as i2
join gdpPacAll g2
on g2.id = i2.id and g2.obsDate = i2.obsDate and g2.obsTime = i2.obsTime
WHERE   NOT EXISTS (SELECT 1 FROM gdpPacAll where id = g2.id and obsdate = '2000-01-01')
  AND     NOT EXISTS (select 1 from gdpPacAll where id = g2.id and obsdate = '2011-03-01');