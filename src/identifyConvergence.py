""" Identify convergence module selects zones in the oceans
    it finds the count of drifters in each zone at t0 and using
    a chi-squared method, compares t0 to t1...n and reports on
    each comparison
"""
import connection
import utils


def newZone(name, latMin, latMax, longMin, longMax):
    """ create a simple dict of long, lat ranges
    """
    return {'name': name, 'latMin': latMin, 'latMax': latMax, 'longMin': longMin, 'longMax': longMax}


def compare(ocean='pacific'):
    conn = connection.new()
    if ocean.lower() == 'atlantic': ocean = 'gdpAtlAll'
    else: ocean = 'gdpPacAll'
    """ sql: give me the ids of all drifters that existed within the bounding coordinates on thier day of deployment
        let min(date) of all ids represent thier deployment date - be sure to exclude day1 of the time period to be
        sure to exclude drifters with start dates before the period in question
    """
    sql = """   SELECT  g1.id
                        ,g1.obsDate
                        ,g1.latitude
                        ,g1.longitude
                FROM    $OCEAN$ g1
                    JOIN    (   SELECT      id
                                            ,min(obsDate) as deployDate
                                            ,date_add(min(obsDate), INTERVAL 400 DAY) as date400 
                                FROM        $OCEAN$
                                GROUP BY    id) as T1
                        ON      g1.id = T1.id
                            AND     g1.obsDate = T1.deployDate
                                AND     g1.obsTime = '12:00'
                
                WHERE   NOT EXISTS (SELECT 1 FROM $OCEAN$ where id = T1.id and obsdate = '2000-01-01')
                    AND     NOT EXISTS (select 1 from $OCEAN$ where id = T1.id and obsdate = '2011-03-01')
                    AND     g1.latitude >= $MINLAT$
                    AND     g1.latitude < $MAXLAT$
                    AND     g1.longitude >= $MINLONG$
                    AND     g1.longitude < $MAXLONG$;
            """
    for zone in gzones:
        query = sql.replace('$OCEAN$', ocean)
        query = query.replace('$MINLAT$', str(zone.get('latMin')))
        query = query.replace('$MAXLAT$', str(zone.get('latMax')))
        query = query.replace('$MINLONG$', str(zone.get('longMin')))
        query = query.replace('$MAXLONG$', str(zone.get('longMax')))
        results = utils.executeMysql_All(conn, query)
        print ('%s: %i' % (zone.get('name'), len(results)))

    sql = """   SELECT  g1.id
                        ,g1.obsDate
                        ,g1.latitude
                        ,g1.longitude
                FROM    $OCEAN$ g1
                    JOIN    (   SELECT      id
                                            ,min(obsDate) as deployDate
                                            ,date_add(min(obsDate), INTERVAL 200 DAY) as date400 
                                FROM        $OCEAN$
                                GROUP BY    id) as T1
                        ON      g1.id = T1.id
                            AND     g1.obsDate = T1.date400
                                AND     g1.obsTime = '12:00'
                
                WHERE   NOT EXISTS (SELECT 1 FROM $OCEAN$ where id = T1.id and obsdate = '2000-01-01')
                    AND     NOT EXISTS (select 1 from $OCEAN$ where id = T1.id and obsdate = '2011-03-01')
                    AND     g1.latitude >= $MINLAT$
                    AND     g1.latitude < $MAXLAT$
                    AND     g1.longitude >= $MINLONG$
                    AND     g1.longitude < $MAXLONG$;
            """
    for zone in gzones:
        query = sql.replace('$OCEAN$', ocean)
        query = query.replace('$MINLAT$', str(zone.get('latMin')))
        query = query.replace('$MAXLAT$', str(zone.get('latMax')))
        query = query.replace('$MINLONG$', str(zone.get('longMin')))
        query = query.replace('$MAXLONG$', str(zone.get('longMax')))
        results = utils.executeMysql_All(conn, query)
        print ('%s: %i' % (zone.get('name'), len(results)))

gzones = [newZone('hawaii', 25, 45, -180, 150),
          newZone('west-pac', 20, 40, 170, 180),
          newZone('japan', 0, 45, 150, 170),
          newZone('north-west', 45, 65, 150, 180),
          newZone('north-east', 45, 65, -180, 130),
          newZone('south-east', 0, 25, -180, 130),
          newZone('south-west', 0, 25, 150, 180),
          ]

if __name__ == '__main__':
    compare()
