SELECT  g1.id
                        ,g1.obsDate
                        ,g1.latitude
                        ,g1.longitude
                FROM    gdpPacAdj g1
                    JOIN    (   SELECT      id
                                            ,date_add(min(obsDate), INTERVAL 0 DAY) as datetime
                                FROM        gdpPacAdj
                                GROUP BY    id) as T1
                        ON      g1.id = T1.id
                            AND     g1.obsDate = T1.datetime
                WHERE   NOT EXISTS (SELECT 1 FROM gdpPacAdj where id = T1.id and obsdate = '2000-01-01')
                    AND     NOT EXISTS (select 1 from gdpPacAdj where id = T1.id and obsdate = '2011-03-01')
                    AND     g1.latitude >= 25
                    AND     g1.latitude < 40
                    AND     g1.longitude >= 140
                    AND     g1.longitude < 160


 25.00001, 40, 140.00001, 160