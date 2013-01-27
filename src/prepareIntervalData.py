import connection
import utils
import os

INTERVALS = range(0, 2001, 100)


def buildQuery(interval, ocean):
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
    """
    query = sql.replace('$OCEAN$', ocean)
    query = query.replace('$INTERVAL$', str(interval))
    return query


def writeData():
    ocean = 'atlantic'
    conn = connection.new()
    f = open(os.path.join(utils.DATA_PATH, 'interval_' + ocean + '.csv'), 'w')
    f.write('id, interval, obsDate, latitude, longitude, longitudeInv\n')
    if ocean.lower() == 'atlantic':
        ocean = 'gdpAtlAdj'
    else:
        ocean = 'gdpPacAdj'

    for interval in INTERVALS:
        query = buildQuery(interval, ocean)
        results = utils.executeMysql_All(conn, query)
        for row in results:
            f.write('%s, %s, %s, %s, %s, %s\n' % (row['id'], interval, row['obsDate'], row['latitude'], row['longitude'], -1 * float(row['longitude'])))


if __name__ == '__main__':
    writeData()
