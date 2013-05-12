select  trim(t100.zone) as zone
        ,fn_significance(t50.f, t100.sig) as t50
        ,fn_significance(t100.f, t100.sig) as t100
        ,fn_significance(t150.f, t100.sig) as t150
        ,fn_significance(t200.f, t200.sig) as t200
        ,fn_significance(t250.f, t100.sig) as t250
        ,fn_significance(t300.f, t300.sig) as t300
        ,fn_significance(t350.f, t100.sig) as t350
        ,fn_significance(t400.f, t400.sig) as t400
        ,fn_significance(t450.f, t100.sig) as t450
        ,fn_significance(t500.f, t500.sig) as t500
        ,fn_significance(t550.f, t100.sig) as t550
        ,fn_significance(t600.f, t600.sig) as t600
        ,fn_significance(t650.f, t100.sig) as t650
        ,fn_significance(t700.f, t700.sig) as t700
        ,fn_significance(t750.f, t100.sig) as t750
        ,fn_significance(t800.f, t800.sig) as t800
        ,fn_significance(t850.f, t100.sig) as t850
        ,fn_significance(t900.f, t900.sig) as t900
        ,fn_significance(t950.f, t100.sig) as t950
        ,fn_significance(t1000.f, t1000.sig) as t1000
        ,fn_significance(t1050.f, t100.sig) as t1050
        ,fn_significance(t1100.f, t1100.sig) as t1100
        ,fn_significance(t1150.f, t100.sig) as t1150
        ,fn_significance(t1200.f, t1200.sig) as t1200 
from ( select fisher as f, sig, zone from fisherResults where period = 100 and ocean = 'gdpAtlAdj') as t100
join ( select fisher as f, sig, zone from fisherResults where period = 200 and ocean = 'gdpAtlAdj') as t200
    on  t100.zone = t200.zone
join ( select fisher as f, sig, zone from fisherResults where period = 300 and ocean = 'gdpAtlAdj') as t300
    on  t100.zone = t300.zone
join ( select fisher as f, sig, zone from fisherResults where period = 400 and ocean = 'gdpAtlAdj') as t400
    on  t100.zone = t400.zone
join ( select fisher as f, sig, zone from fisherResults where period = 500 and ocean = 'gdpAtlAdj') as t500
    on  t100.zone = t500.zone
join ( select fisher as f, sig, zone from fisherResults where period = 600 and ocean = 'gdpAtlAdj') as t600
    on  t100.zone = t600.zone
join ( select fisher as f, sig, zone from fisherResults where period = 700 and ocean = 'gdpAtlAdj') as t700
    on  t100.zone = t700.zone
join ( select fisher as f, sig, zone from fisherResults where period = 800 and ocean = 'gdpAtlAdj') as t800
    on  t100.zone = t800.zone
join ( select fisher as f, sig, zone from fisherResults where period = 900 and ocean = 'gdpAtlAdj') as t900
    on  t100.zone = t900.zone
join ( select fisher as f, sig, zone from fisherResults where period = 1000 and ocean = 'gdpAtlAdj') as t1000
    on  t100.zone = t1000.zone
join ( select fisher as f, sig, zone from fisherResults where period = 1100 and ocean = 'gdpAtlAdj') as t1100
    on  t100.zone = t1100.zone
join ( select fisher as f, sig, zone from fisherResults where period = 1200 and ocean = 'gdpAtlAdj') as t1200
    on  t100.zone = t1200.zone
join ( select fisher as f, sig, zone from fisherResults where period = 50 and ocean = 'gdpAtlAdj') as t50
    on  t100.zone = t50.zone
join ( select fisher as f, sig, zone from fisherResults where period = 150 and ocean = 'gdpAtlAdj') as t150
    on  t100.zone = t150.zone
join ( select fisher as f, sig, zone from fisherResults where period = 250 and ocean = 'gdpAtlAdj') as t250
    on  t100.zone = t250.zone
join ( select fisher as f, sig, zone from fisherResults where period = 350 and ocean = 'gdpAtlAdj') as t350
    on  t100.zone = t350.zone
join ( select fisher as f, sig, zone from fisherResults where period = 450 and ocean = 'gdpAtlAdj') as t450
    on  t100.zone = t450.zone
join ( select fisher as f, sig, zone from fisherResults where period = 550 and ocean = 'gdpAtlAdj') as t550
    on  t100.zone = t550.zone
join ( select fisher as f, sig, zone from fisherResults where period = 650 and ocean = 'gdpAtlAdj') as t650
    on  t100.zone = t650.zone
join ( select fisher as f, sig, zone from fisherResults where period = 750 and ocean = 'gdpAtlAdj') as t750
    on  t100.zone = t750.zone
join ( select fisher as f, sig, zone from fisherResults where period = 850 and ocean = 'gdpAtlAdj') as t850
    on  t100.zone = t850.zone
join ( select fisher as f, sig, zone from fisherResults where period = 950 and ocean = 'gdpAtlAdj') as t950
    on  t100.zone = t950.zone
join ( select fisher as f, sig, zone from fisherResults where period = 1050 and ocean = 'gdpAtlAdj') as t1050
    on  t100.zone = t1050.zone
join ( select fisher as f, sig, zone from fisherResults where period = 1150 and ocean = 'gdpAtlAdj') as t1150
    on  t100.zone = t1150.zone

order by trim(zone) desc