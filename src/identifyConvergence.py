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
    sql = """   SELECT      id, min(obsDate)
                FROM        $OCEAN$
                WHERE       latitude >= $MINLAT$
                    and latitude < $MAXLAT$
                    and longitude >= $MINLONG$
                    and longitude < $MAXLONG$
            """
    for zone in gzones:
        query = sql.replace('$OCEAN$', ocean)
        query = query.replace('$MINLAT$', str(zone.get('latMin')))
        query = query.replace('$MAXLAT$', str(zone.get('latMax')))
        query = query.replace('$MINLONG$', str(zone.get('longMin')))
        query = query.replace('$MAXLONG$', str(zone.get('longMax')))
        print query
        results = utils.executeMysql_All(conn, query)
        print ('%s: %i' % (zone.get('name'), len(results)))

gzones = [newZone('hawaii', 25, 45, -180, 150),
          newZone('west-pac', 20, 40, 170, 180)
          ]

if __name__ == '__main__':
    compare()
