""" drifter lifespan
    This module will aim to query the db and produce statistics on mortaility of drifters
    basic procedure will be to gather the min and max date of each drifter, calculate its
    lifespan, and create a table with all lifespans.
    I will need to examine any anomolies, for some drifter numbers can be re-used. Any
    drifter surviving too long should be looked at further for gaps that would indicate
    re-use
"""
import connection
import utils
import os


def buildLifeTable(ocean='pacific'):
    conn = connection.new()
    f = open(os.path.join(utils.DATA_PATH, 'lifespan_' + ocean + '.csv'), 'w')
    if ocean.lower() == 'atlantic': ocean = 'gdpAtlAdj'
    else: ocean = 'gdpPacAdj'
    
    sql = """ SELECT * FROM (
                  SELECT  id
                          ,min(obsdate) as min
                          ,max(obsdate) as max
                          ,datediff(max(obsdate), min(obsdate)) as age
                  FROM    $OCEAN$ t
                  WHERE   obsdate >= '2000-01-01'
                      AND     obsdate <= '2011-03-01'
                  GROUP BY  id) AS i
                WHERE     NOT EXISTS (select 1 from $OCEAN$ where id = i.id and obsdate = '2000-01-01')
                  AND     NOT EXISTS (select 1 from $OCEAN$ where id = i.id and obsdate = '2011-03-01');
        """
    results = utils.executeMysql_All(conn, sql.replace('$OCEAN$', ocean))
    lifespans = {}

    drifterCount = len(results)

    for row in results:
        age = row.get('age')
        if age in lifespans:
            lifespans[age] = lifespans[age] + 1
        else:
            lifespans[age] = 1

    mortalityIntervals = range(0, 100, 10) + range(100, 2001, 100)
    for i in mortalityIntervals:
        bodycount = 0
        for age, count in lifespans.items():
            if age < i:
                bodycount += count
        mortalityRate = (float(bodycount) / drifterCount)
        numberAlive = drifterCount - bodycount
        percentAlive = 1.0 - mortalityRate
        print('%i, %.5f, %i, %.5f' % (i, mortalityRate, numberAlive, percentAlive))
        f.write('%i, %.5f, %i, %.5f\n' % (i, mortalityRate, numberAlive, percentAlive))


# what percent of drifters die after X number of days
if __name__ == '__main__':
    print "Pacific Drifter LifeTable"
    buildLifeTable()
    print "Atlantic Drifter LifeTable"
    buildLifeTable('atlantic')
