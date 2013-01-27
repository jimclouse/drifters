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

INTERVALS = range(100, 1401, 100)


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


def compare(zoneList, ocean='pacific'):
    """ creates a one-way chi-squared table of all intervals for each zone
    """
    conn = connection.new()
    lifetable = buildLifeTable(ocean.lower())
    if ocean.lower() == 'atlantic':
        ocean = 'gdpAtlAdj'
    else:
        ocean = 'gdpPacAdj'

    for zone in zoneList:
        print("** Zone Summary: %s" % (zone.get('name')))
        print("** %s:%sN, %s:%sE" % (zone.get('latMin'), zone.get('latMax'), zone.get('longMin'), zone.get('longMax')))
        baseline = utils.executeMysql_All(conn, buildQuery(ocean, zone, 0))
        baselineCount = len(baseline)
        expected = []
        observed = []
        for interval in INTERVALS:
            results = utils.executeMysql_All(conn, buildQuery(ocean, zone, interval))
            expectedValue = int(baselineCount * (1 - lifetable.get(interval)))
            observedValue = int(len(results))
            if observedValue >= 5 and expectedValue >= 5:
                expected.append(expectedValue)
                observed.append(observedValue)
                print('%s (%s): baseline: %i, adjBase: %i, obs: %i'
                      % (zone.get('name'), interval, baselineCount, expectedValue, observedValue))
            else:
                print('%s (%s): ignored because of low values. baseline: %i, adjBase: %i, obs: %i'
                      % (zone.get('name'), interval, baselineCount, expectedValue, observedValue))

        chi = chisquare(np.array(observed), np.array(expected))
        print("** Chi-Squared Statistic: %f, p=%s" % (chi[0], chi[1]))
        print("**")


def compare2(zoneList, ocean='pacific'):
    """ creates a one-way chi-squared table of all zones for each interval
    """
    conn = connection.new()
    lifetable = buildLifeTable(ocean.lower())
    if ocean.lower() == 'atlantic':
        ocean = 'gdpAtlAdj'
    else:
        ocean = 'gdpPacAdj'

    for interval in INTERVALS:
        print("** %s Day Interval Summary" % (interval))
        expected = []
        observed = []
        for zone in zoneList:
            zoneBaseline = utils.executeMysql_All(conn, buildQuery(ocean, zone, 0))
            zoneBaselineCount = len(zoneBaseline)
            results = utils.executeMysql_All(conn, buildQuery(ocean, zone, interval))
            expectedValue = int(zoneBaselineCount * (1 - lifetable.get(interval)))
            observedValue = int(len(results))
            if observedValue >= 5 and expectedValue >= 5:
                expected.append(expectedValue)
                observed.append(observedValue)
                print('%s (%s): baseline: %i, adjBase: %i, obs: %i'
                      % (zone.get('name'), interval, zoneBaselineCount, expectedValue, observedValue))
            else:
                print('%s (%s): ignored because of low values. baseline: %i, adjBase: %i, obs: %i'
                      % (zone.get('name'), interval, zoneBaselineCount, expectedValue, observedValue))

        if len(expected) == 0:
            print("** No data for interval %s available" % (interval))
        else:
            chi = chisquare(np.array(observed), np.array(expected))
            print("** Chi-Squared Statistic: %f, p=%s" % (chi[0], chi[1]))
        print("**")


if __name__ == '__main__':

    ZONES_PAC = [newZone('hawaii', 25, 40, 127, 180),
                 newZone('north-east', 35, 65, 125, 180),
                 newZone('california', 25, 40, 115, 127),
                 newZone('south-east', 0, 25, 80, 180),

                 newZone('west-pac', 20, 35, -170, -155),
                 newZone('north-west', 35, 65, -180, -120),
                 newZone('japan', 20, 35, -155, -115),
                 newZone('south-west', 0, 20, -180, -115)
                 ]

    ZONES_ATL = [newZone('sargasso', 24, 35, 50, 70),
                 newZone('north-west', 35, 65, 50, 82),
                 newZone('east-coast', 24, 35, 70, 82),
                 newZone('south-west', 0, 24, 50, 82),

                 newZone('east-atl', 27, 40, 25, 40),
                 newZone('north-east', 40, 65, 0, 50),
                 newZone('europe', 27, 40, 0, 25),
                 newZone('south-east', 0, 27, -8, 50),
                 newZone('middle-atlantic', 27, 40, 40, 50)
                 ]

    ZONES_SARGASO_1_DEG = [newZone('s1', 34.00001, 35, 50, 70),
                           newZone('s1', 33.00001, 34, 50, 70),
                           newZone('s1', 32.00001, 33, 50, 70),
                           newZone('s1', 31.00001, 32, 50, 70),
                           newZone('s1', 30.00001, 31, 50, 70),
                           newZone('s1', 29.00001, 30, 50, 70),
                           newZone('s1', 28.00001, 29, 50, 70),
                           newZone('s1', 27.00001, 28, 50, 70),
                           newZone('s1', 26.00001, 27, 50, 70),
                           newZone('s1', 25.00001, 26, 50, 70),
                           newZone('s1', 24, 25, 50, 70)]

    ZONES_SARGASO_2_DEG = [newZone('s1', 40.00001, 42, 50, 70),
                           newZone('s2', 38.00001, 40, 50, 70),
                           newZone('s3', 36.00001, 38, 50, 70),
                           newZone('s4', 34.00001, 36, 50, 70),
                           newZone('s5', 32.00001, 34, 50, 70),
                           newZone('s6', 30.00001, 32, 50, 70),
                           newZone('s7', 28.00001, 30, 50, 70),
                           newZone('s8', 26.00001, 28, 50, 70),
                           newZone('s9', 24.00001, 26, 50, 70),
                           newZone('s10', 22.00001, 24, 50, 70)]

    compare(ZONES_SARGASO_2_DEG, ocean='atlantic')
