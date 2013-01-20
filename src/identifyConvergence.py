""" Identify convergence module selects zones in the oceans
    it finds the count of drifters in each zone at t0 and using
    a chi-squared method, compares t0 to t1...n and reports on
    each comparison
"""
import connection
import utils
import os
import csv
from scipy.stats import chisquare
import numpy as np

lifespan_atlantic = {}
lifespan_pacific = {}


def newZone(name, latMin, latMax, longMin, longMax):
    """ create a simple dict of long, lat ranges
    """
    return {'name': name, 'latMin': latMin, 'latMax': latMax, 'longMin': longMin, 'longMax': longMax}


def buildLifeTable(ocean):
    """ pull down lifetable data and place in dictionary for calculations
    """
    lifetable = {}
    f = csv.reader(open(os.path.join(utils.DATA_PATH, 'lifespan_' + ocean + '.csv'), 'r'))
    for row in f:
        lifetable[int(row[0])] = float(row[1])
    return lifetable


def buildQuery(ocean, zone, interval):
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
                                            ,date_add(min(obsDate), INTERVAL $INTERVAL$ DAY) as datetime
                                FROM        $OCEAN$
                                GROUP BY    id) as T1
                        ON      g1.id = T1.id
                            AND     g1.obsDate = T1.datetime
                WHERE   NOT EXISTS (SELECT 1 FROM $OCEAN$ where id = T1.id and obsdate = '2000-01-01')
                    AND     NOT EXISTS (select 1 from $OCEAN$ where id = T1.id and obsdate = '2011-03-01')
                    AND     g1.latitude >= $MINLAT$
                    AND     g1.latitude < $MAXLAT$
                    AND     g1.longitude >= $MINLONG$
                    AND     g1.longitude < $MAXLONG$;
            """
    query = sql.replace('$OCEAN$', ocean)
    query = query.replace('$MINLAT$', str(zone.get('latMin')))
    query = query.replace('$MAXLAT$', str(zone.get('latMax')))
    query = query.replace('$MINLONG$', str(zone.get('longMin')))
    query = query.replace('$MAXLONG$', str(zone.get('longMax')))
    query = query.replace('$INTERVAL$', str(interval))

    return query


def compare(ocean='pacific'):
    conn = connection.new()
    lifetable = buildLifeTable(ocean.lower())
    if ocean.lower() == 'atlantic':
        ocean = 'gdpAtlAdj'
    else:
        ocean = 'gdpPacAdj'

    for zone in GZONES:
        query = buildQuery(ocean, zone, 0)
        baseline = utils.executeMysql_All(conn, query)
        baselineCount = len(baseline)
        expected = []
        observed = []
        for interval in INTERVALS:
            query = buildQuery(ocean, zone, interval)
            results = utils.executeMysql_All(conn, query)
            expectedValue = int(baselineCount - (baselineCount * lifetable.get(interval)))
            observedValue = int(len(results))
            if observedValue >= 5 and expectedValue >= 5:
                expected.append(expectedValue)
                observed.append(observedValue)
            else:
                print "expected value of 0 found, value not added to chi-squared model"
            print ('%s (%s): baseline: %i, adjBase: %i, obs: %i'
                   % (zone.get('name'), interval, baselineCount, expectedValue, observedValue))
        print("** Zone Summary: %s" % (zone.get('name')))
        chi = chisquare(np.array(expected), np.array(observed))
        print("** %f p=%s" % (chi[0], chi[1]))
        print("**")

## Global vars. down here so they can make use of methods
## coordinates of zones we're doing comparisons on.
GZONES = [newZone('hawaii', 25, 45, -180, 150),
          newZone('west-pac', 20, 40, 170, 180),
          newZone('japan', 0, 45, 150, 170),
          newZone('north-west', 45, 65, 150, 180),
          newZone('north-east', 45, 65, -180, 130),
          newZone('south-east', 0, 25, -180, 130),
          newZone('south-west', 0, 25, 150, 180),
          ]

INTERVALS = range(100, 2001, 100)

if __name__ == '__main__':
    compare(ocean='pacific')
