select  trim(t100.zone) as zone
        ,round(t100.r,2) as t100
        ,round(t200.r,2) as t200
        ,round(t300.r,2) as t300 
        ,round(t400.r,2) as t400 
        ,round(t500.r,2) as t500 
        ,round(t600.r,2) as t600 
        ,round(t700.r,2) as t700 
        ,round(t800.r,2) as t800 
        ,round(t900.r,2) as t900 
        ,round(t1000.r,2) as t1000 
        ,round(t1100.r,2) as t1100 
        ,round(t1200.r,2) as t1200 
from ( select residual as r, zone from chiResiduals where period = 100 and ocean = 'gdpAtlAdj') as t100
join ( select residual as r, zone from chiResiduals where period = 200 and ocean = 'gdpAtlAdj') as t200
    on  t100.zone = t200.zone
join ( select residual as r, zone from chiResiduals where period = 300 and ocean = 'gdpAtlAdj') as t300
    on  t100.zone = t300.zone
join ( select residual as r, zone from chiResiduals where period = 400 and ocean = 'gdpAtlAdj') as t400
    on  t100.zone = t400.zone
join ( select residual as r, zone from chiResiduals where period = 500 and ocean = 'gdpAtlAdj') as t500
    on  t100.zone = t500.zone
join ( select residual as r, zone from chiResiduals where period = 600 and ocean = 'gdpAtlAdj') as t600
    on  t100.zone = t600.zone
join ( select residual as r, zone from chiResiduals where period = 700 and ocean = 'gdpAtlAdj') as t700
    on  t100.zone = t700.zone
join ( select residual as r, zone from chiResiduals where period = 800 and ocean = 'gdpAtlAdj') as t800
    on  t100.zone = t800.zone
join ( select residual as r, zone from chiResiduals where period = 900 and ocean = 'gdpAtlAdj') as t900
    on  t100.zone = t900.zone
join ( select residual as r, zone from chiResiduals where period = 1000 and ocean = 'gdpAtlAdj') as t1000
    on  t100.zone = t1000.zone
join ( select residual as r, zone from chiResiduals where period = 1100 and ocean = 'gdpAtlAdj') as t1100
    on  t100.zone = t1100.zone
join ( select residual as r, zone from chiResiduals where period = 1200 and ocean = 'gdpAtlAdj') as t1200
    on  t100.zone = t1200.zone
order by trim(zone)