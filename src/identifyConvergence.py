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


def newZone(name, latMin, latMax, longMin, longMax, extraCoords=None):
    """ create a simple dict of long, lat ranges
    """
    return {'name': name, 'latMin': latMin, 'latMax': latMax, 'longMin': longMin, 'longMax': longMax, 'extraCoords': extraCoords}


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


def compare_incorrect(zoneList, ocean='pacific'):
    """ creates a one-way chi-squared table of all intervals for each zone
        after discussing with Mark, this is the incorrect way to approach this chi-squared comparison
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


def getCountOfExtraCoords(conn, zone, ocean, interval):
    coordinatesList = zone.get('extraCoords')
    totalCount = 0
    for t in coordinatesList:
        r = utils.executeMysql_All(conn, buildQuery(ocean, newZone("na", t[0], t[1], t[2], t[3]), 0))
        totalCount += len(r)
    return totalCount


def compare(zoneList, ocean='pacific'):
    """ creates a one-way chi-squared table of all zones for each interval
        1. for each zone, get the percentage of all drifters that exist in it for the baseline
            a. find the total number
            b. loop through all zones and compute ratios
            c. this is the expected ratio
        2. do the same for each time period
            a. find the total number of drifters alive
            b. compute the ratio of drifters in each zone
            c. this is the observed ratio
            d. use the expected ratio and observed ratio to calculate expected and observed counts for each zone

        this results in a 9x2 table
                z1 | z2 | z3 | ...
        obs |   x  | ...
        exp |   y  | ...
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
            zoneBaselineValue = len(zoneBaseline)
            zoneObserved = utils.executeMysql_All(conn, buildQuery(ocean, zone, interval))
            observedValue = int(len(zoneObserved))
            if zone.get('extraCoords'):
                zoneBaselineValue = zoneBaselineValue + getCountOfExtraCoords(conn, zone, ocean, 0)
                observedValue = observedValue + getCountOfExtraCoords(conn, zone, ocean, interval)

            expectedValue = int(zoneBaselineValue * (1 - lifetable.get(interval)))

            if observedValue >= 5 and expectedValue >= 5:
                expected.append(expectedValue)
                observed.append(observedValue)
                print('%s (%s): baseline: %i, adjBase: %i, obs: %i'
                      % (zone.get('name'), interval, zoneBaselineValue, expectedValue, observedValue))
            else:
                print('%s (%s): ignored because of low values. baseline: %i, adjBase: %i, obs: %i'
                      % (zone.get('name'), interval, zoneBaselineValue, expectedValue, observedValue))

        if len(expected) == 0:
            print("** No data for interval %s available" % (interval))
        else:
            chi = chisquare(np.array(observed), np.array(expected))
            print("** Chi-Squared Statistic: %f, p=%s" % (chi[0], chi[1]))
        print("**")


if __name__ == '__main__':

    ZONES_PAC = [newZone('hawaii-convergence', 25.00001, 40, 127.00001, 180),
                 newZone('north-east', 35.00001, 65, 125.00001, 180),
                 newZone('california', 25.00001, 40, 115.00001, 127),
                 newZone('south-east', 0.00001, 25, 80.00001, 180),
                 newZone('west-pacific-convergence', 20.00001, 35, -165.00001, -150),
                 newZone('north-west', 35.00001, 65, -180.00001, -120),
                 newZone('japan', 20.00001, 35, -150.00001, -115),
                 newZone('south-west', 0.00001, 20, -180.00001, -115),
                 newZone('central-pac-convergence', 20.00001, 35, -180.00001, -165, [(25.00001, 40, 160.00001, 180)])
                 ]

    ZONES_ATL = [newZone('sargasso-convergence', 24.00001, 35, 50.00001, 70),
                 newZone('north-west', 35.00001, 65, 50.00001, 82),
                 newZone('east-coast', 24.00001, 35, 70.00001, 82),
                 newZone('south-west', 0.00001, 24, 50.00001, 82),
                 newZone('east-atlantic-convergence', 27.00001, 40, 25.00001, 40),
                 newZone('north-east', 40.00001, 65, 0.00001, 50),
                 newZone('europe', 27.00001, 40, 0.00001, 25),
                 newZone('south-east', 0.00001, 27, -8.00001, 50),
                 newZone('central-atlantic-convergence', 27.00001, 40, 40.00001, 50)
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

    compare(ZONES_PAC, ocean='pacific')
