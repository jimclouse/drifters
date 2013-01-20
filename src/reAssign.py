""" Look for gaps in the drifter date ranges and give new ID numbers to the new set of dates
    Every time we hit a large enough gap, assign a new ID
"""
import connection
import utils
import os

MAX_GAP = 20


def adjust(dataPath, basin):
    conn = connection.new()
    fileName = os.path.join(dataPath, "gdp" + basin + "All_adjusted.csv")
    rFile = open(fileName, 'w')
    dbTable = 'gdp' + basin + 'All'

    sql = """ SELECT g.id, g.obsDate, g.obsTime, latitude, longitude
                from (SELECT id, ObsDate, max(ObsTime) as ObsTime from $dbTable$
                group by id, obsDate) as i join $dbTable$ g
                on i.id = g.id and i.obsDate = g.obsDate and i.obsTime = g.obsTime
                where g.obsDate >= '2000-01-01'
                order by g.id, g.ObsDate
        """
    print sql
    sql = sql.replace('$dbTable$', dbTable)
    print "running query"
    results = utils.executeMysql_All(conn, sql)
    print "query complete. processing"
    prevId = None
    prevDate = None
    seriesList = ['x', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    for row in results:
        id = row['id']
        obsDate = row['obsDate']
        obsTime = row['obsTime']
        Lat = row['latitude']
        Long = row['longitude']
        # reset on each new Id
        if not id == prevId:
            prevId = id
            prevDate = None
            newId = id
            seriesIndex = 0

        # look for gaps
        if (not prevDate is None):
            diff = obsDate - prevDate
            if diff.days > MAX_GAP:
                print("gap! %i days") % (diff.days)
                seriesIndex += 1
                newId = str(id) + seriesList[seriesIndex]
        prevDate = obsDate
        rFile.write('%s, %s, %s, %s, %s\n' % (newId, obsDate, obsTime, Lat, Long))

        sql = "alter table " + dbTable + " add index(id)"
        utils.executeMysql_Command(conn, sql)

adjust(utils.DATA_PATH_ATL, 'Atl')
