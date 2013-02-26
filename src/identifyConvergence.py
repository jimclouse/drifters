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
from scipy.stats import fisher_exact
import numpy as np

lifespan_atlantic = {}
lifespan_pacific = {}

INTERVALS = range(0, 1201, 100)


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

        Null Hypothesis: Each zone has an evenly distributed probability of occuring
        Alt Hypothesis: At least one of the proportions is different from predicted

    """
    conn = connection.new()
    #lifetable = buildLifeTable(ocean.lower())
    if ocean.lower() == 'atlantic':
        ocean = 'gdpAtlAdj'
    else:
        ocean = 'gdpPacAdj'

    # clean fishers results table
    sql = "delete from fisherResults where ocean = '" + ocean + "';"
    utils.executeMysql_All(conn, sql)
    sql = "delete from chiSquareResults where ocean = '" + ocean + "';"
    utils.executeMysql_All(conn, sql)

    # get baseline data for each zone
    for zone in zoneList:
        zone["baselineCount"] = len(utils.executeMysql_All(conn, buildQuery(ocean, zone, 0)))
        if zone.get('extraCoords'):
            zone["baselineCount"] = zone.get("baselineCount", 0) + getCountOfExtraCoords(conn, zone, ocean, 0)

    # get total drifter count
    baselineDrifterCount = 0
    for zone in zoneList:
        baselineDrifterCount = baselineDrifterCount + zone.get("baselineCount")

    # define baseline ratios
    for zone in zoneList:
        zone["baselineRatio"] = zone.get("baselineCount") / float(baselineDrifterCount)
        print zone.get("baselineRatio")

    # loop through intervals, running chi-square at each interval
    for interval in INTERVALS:
        print("********************************")
        print("** %s Day Interval Summary **" % (interval))
        expected = []
        observed = []

        # get interval zone counts
        for zone in zoneList:
            zone["intervalObserved"] = len(utils.executeMysql_All(conn, buildQuery(ocean, zone, interval)))
            if zone.get('extraCoords'):
                zone["intervalObserved"] = zone.get("intervalObserved", 0) + getCountOfExtraCoords(conn, zone, ocean, interval)

        # get total interval count
        totalObserved = 0
        for zone in zoneList:
            totalObserved = totalObserved + zone.get("intervalObserved")

        # collect obs & exp data into list for each zone
        for zone in zoneList:
            intervalExpected = totalObserved * zone.get("baselineRatio")
            zone["intervalExpected"] = intervalExpected
            #if observedValue >= 5 and expectedValue >= 5:
            expected.append(intervalExpected)
            observed.append(zone.get("intervalObserved"))
            print('%s: baseline ratio: %f, no. drifters: %i, expected: %f, observed: %f'
                  % (zone.get('name'), zone.get("baselineRatio"), totalObserved, intervalExpected, zone.get("intervalObserved")))
            # else:
            #     print('%s (%s): ignored because of low values. baseline: %i, adjBase: %i, obs: %i'
            #           % (zone.get('name'), interval, zoneBaselineValue, expectedValue, observedValue))

        # perform and report on chi-square
        if len(expected) == 0:
            print("** No data for interval %s available" % (interval))
        else:
            chi = chisquare(np.array(observed), np.array(expected))
            print("** Chi-Squared Statistic: %f, p=%s" % (chi[0], chi[1]))
            sql = "insert into chiSquareResults (ocean, period, chiStat, sig, sigStr) values('" + ocean + "', '" + str(interval) + "', " + str(chi[0]) + ", " + str("{0:.4f}".format(float(chi[1]))) + ", '" + str(float(chi[1])) + "')"
            print sql
            utils.executeMysql_All(conn, sql)
        print("**")

        for zone in zoneList:
            # perform Fisher's Exact Test on each zone to determine differnce with rest of data
            fishers(ocean, conn, interval, zone, zone.get("intervalExpected"), zone.get("intervalObserved"), baselineDrifterCount)

        print("\n\n")


def formatOdds(val):
    val = str(val)
    if val == 'inf': return '9999'
    return "{0:.3f}".format(float(val))


def fishers(ocean, conn, interval, zone, zoneExpected, zoneObserved, globalCount):
    """ The null hypothesis is that the relative proportions of one variable are independent
        of the second variable. For example, if you counted the number of male and female mice
        in two barns, the null hypothesis would be that the proportion of male mice is the
        same in the two barns.
        http://udel.edu/~mcdonald/statfishers.html
        inputs: zone expected, zone observed, not zone expected, not zone observed
                in zone     not in zone
    observed    a           b
    expected    c           d
    """
    notZoneExpected = globalCount - zoneExpected
    notZoneObserved = globalCount - zoneObserved

    if zoneExpected < 1 and zoneObserved == 0:
        print("** values too low")
    else:
        odds, pval = fisher_exact(np.array([[zoneObserved, notZoneObserved], [zoneExpected, notZoneExpected]]))
        sql = "insert into fisherResults (ocean, zone, period, fisher, sig) values('" + ocean + "', '" + zone.get('name') + "', '" + str(interval) + "', " + formatOdds(odds) + ", " + str(pval) + ")"
        utils.executeMysql_All(conn, sql)
        print("** Fishers Exact: %s: odds: %s, p: %s" % (zone.get('name'), formatOdds(odds), pval))


if __name__ == '__main__':
    """ main method. defines zones and runs main executable
    """
    ZONES_PAC = [newZone('      Hawaii-convergence', 25.00001, 40, 140.00001, 160),
                 newZone(' Central-pac-convergence', 25.00001, 40, 160.00001, 180),
                 newZone('West-pacific-convergence', 20.00001, 35, -180.00001, -160),
                 newZone('              North-east', 40.00001, 60, 120.00001, 180),
                 newZone('              California', 25.00001, 40, 115.00001, 140),
                 newZone('              South-east', 0.00001, 25, 75.00001, 180),
                 newZone('              South-west', 0.00001, 20, -180.00001, -100),
                 newZone('                   Japan', 20.00001, 35, -160.00001, -100),
                 newZone('              North-west', 35.00001, 60, -180.00001, -100)
                 ]

    ZONES_ATL = [newZone('        Sargasso-convergence', 20.00001, 35, 50.00001, 70),
                 newZone('Central-atlantic-convergence', 27.00001, 40, 40.00001, 50),
                 newZone('   East-atlantic-convergence', 27.00001, 40, 25.00001, 40),
                 newZone('                  North-east', 40.00001, 60, 0.00001, 50),
                 newZone('                      Europe', 27.00001, 40, 0.00001, 25),
                 newZone('                  South-east', 0.00001, 27, -8.00001, 50),
                 newZone('                  South-west', 0.00001, 20, 50.00001, 82),
                 newZone('                  East-coast', 20.00001, 35, 70.00001, 82),
                 newZone('                  North-west', 35.00001, 60, 50.00001, 82)
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

    compare(ZONES_ATL, ocean='atlantic')
    #compare(ZONES_PAC, ocean='pacific')
