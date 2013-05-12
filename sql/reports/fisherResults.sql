select  trim(t100.zone) as zone
        ,fn_significance(t100.f, t100.sig) as t100
        ,fn_significance(t200.f, t200.sig) as t200
        ,fn_significance(t300.f, t300.sig) as t300 
        ,fn_significance(t400.f, t400.sig) as t400 
        ,fn_significance(t500.f, t500.sig) as t500 
        ,fn_significance(t600.f, t600.sig) as t600 
        ,fn_significance(t700.f, t700.sig) as t700 
        ,fn_significance(t800.f, t800.sig) as t800 
        ,fn_significance(t900.f, t900.sig) as t900 
        ,fn_significance(t1000.f, t1000.sig) as t1000 
        ,fn_significance(t1100.f, t1100.sig) as t1100 
        ,fn_significance(t1200.f, t1200.sig) as t1200 
from ( select percent, zone from fisherResults where period = 100 and ocean = 'gdpPacAdj') as t100
join ( select percent, zone from fisherResults where period = 200 and ocean = 'gdpPacAdj') as t200
    on  t100.zone = t200.zone
join ( select percent, zone from fisherResults where period = 300 and ocean = 'gdpPacAdj') as t300
    on  t100.zone = t300.zone
join ( select percent, zone from fisherResults where period = 400 and ocean = 'gdpPacAdj') as t400
    on  t100.zone = t400.zone
join ( select percent, zone from fisherResults where period = 500 and ocean = 'gdpPacAdj') as t500
    on  t100.zone = t500.zone
join ( select percent, zone from fisherResults where period = 600 and ocean = 'gdpPacAdj') as t600
    on  t100.zone = t600.zone
join ( select percent, zone from fisherResults where period = 700 and ocean = 'gdpPacAdj') as t700
    on  t100.zone = t700.zone
join ( select percent, zone from fisherResults where period = 800 and ocean = 'gdpPacAdj') as t800
    on  t100.zone = t800.zone
join ( select percent, zone from fisherResults where period = 900 and ocean = 'gdpPacAdj') as t900
    on  t100.zone = t900.zone
join ( select percent, zone from fisherResults where period = 1000 and ocean = 'gdpPacAdj') as t1000
    on  t100.zone = t1000.zone
join ( select percent, zone from fisherResults where period = 1100 and ocean = 'gdpPacAdj') as t1100
    on  t100.zone = t1100.zone
join ( select percent, zone from fisherResults where period = 1200 and ocean = 'gdpPacAdj') as t1200
    on  t100.zone = t1200.zone
order by trim(zone)