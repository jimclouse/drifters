""" Look for gaps in the drifter date ranges and give new ID numbers to the new set of dates
    Every time we hit a large enough gap, assign a new ID
"""
import connection
import utils

MAX_GAP = 20

conn = connection.new()
rFile = open("gdpPacAll_adjusted.txt", 'w')
sql = """ SELECT g.id, g.obsDate, g.obsTime, latitude, longitude
            from (SELECT id, ObsDate, max(ObsTime) as ObsTime from gdpPacAll
            group by id, obsDate) as i join gdpPacAll g
            on i.id = g.id and i.obsDate = g.obsDate and i.obsTime = g.obsTime
            order by g.id, g.ObsDate
    """
print "running query"
results = utils.executeMysql_All(conn, sql)
print "query complete. processing"
fmt = '%Y-%m-%d %H:%M:%S'
prevId = None
prevDate = None
seriesList = ['x', 'a', 'b', 'c', 'd', 'e']
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
