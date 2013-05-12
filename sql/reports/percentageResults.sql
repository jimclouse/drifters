select  trim(t100.zone) as zone
        ,format(t0.percent, 4) as t0
        ,format(t100.percent, 4) as t100
        ,format(t200.percent, 4) as t200
        ,format(t300.percent, 4) as t300 
        ,format(t400.percent, 4) as t400 
        ,format(t500.percent, 4) as t500 
        ,format(t600.percent, 4) as t600 
        ,format(t700.percent, 4) as t700 
        ,format(t800.percent, 4) as t800 
        ,format(t900.percent, 4) as t900 
        ,format(t1000.percent, 4) as t1000 
        ,format(t1100.percent, 4) as t1100 
        ,format(t1200.percent, 4) as t1200 
from ( select percent, zone from percentages where period = 100 and ocean = 'gdpAtlAdj') as t100
join ( select percent, zone from percentages where period = 0 and ocean = 'gdpAtlAdj') as t0
    on  t100.zone = t0.zone
join ( select percent, zone from percentages where period = 200 and ocean = 'gdpAtlAdj') as t200
    on  t100.zone = t200.zone
join ( select percent, zone from percentages where period = 300 and ocean = 'gdpAtlAdj') as t300
    on  t100.zone = t300.zone
join ( select percent, zone from percentages where period = 400 and ocean = 'gdpAtlAdj') as t400
    on  t100.zone = t400.zone
join ( select percent, zone from percentages where period = 500 and ocean = 'gdpAtlAdj') as t500
    on  t100.zone = t500.zone
join ( select percent, zone from percentages where period = 600 and ocean = 'gdpAtlAdj') as t600
    on  t100.zone = t600.zone
join ( select percent, zone from percentages where period = 700 and ocean = 'gdpAtlAdj') as t700
    on  t100.zone = t700.zone
join ( select percent, zone from percentages where period = 800 and ocean = 'gdpAtlAdj') as t800
    on  t100.zone = t800.zone
join ( select percent, zone from percentages where period = 900 and ocean = 'gdpAtlAdj') as t900
    on  t100.zone = t900.zone
join ( select percent, zone from percentages where period = 1000 and ocean = 'gdpAtlAdj') as t1000
    on  t100.zone = t1000.zone
join ( select percent, zone from percentages where period = 1100 and ocean = 'gdpAtlAdj') as t1100
    on  t100.zone = t1100.zone
join ( select percent, zone from percentages where period = 1200 and ocean = 'gdpAtlAdj') as t1200
    on  t100.zone = t1200.zone
order by trim(zone);