""" export cohorts
    several groups, or cohorts of drifters was selected and plotted in ArcGIS
    for both pacific and atlantic. This script provides a quick method of
    exporting drifter data for these plots
"""
import connection
import utils

PAC_TEMPLATE = """ SELECT 'id', 'obsDate', 'obstime', 'latitude', 'longitude'
                    union select id, obsDate, obstime, latitude, -1*longitude
                        into outfile '$PATH$/pac_drifters_$RANGE$_day_$END_DATE$.csv'
                        FIELDS TERMINATED BY ','
                        LINES TERMINATED BY '\\r\\n'
                    from gdpPacAdj g
                    where exists (  select  1 from gdpPacAdj s1
                                    where s1.id = g.id
                                        and     s1.obsDate = '$START_DATE$'
                                        and     s1.latitude >= 0
                                        and     s1.latitude <= 60
                                        and     ( s1.longitude between 130 and 180
                                            or      s1.longitude between -115 and -180)
                                    )
                        and exists ( select 1 from gdpPacAdj s2
                                    where s2.id = g.id
                                        and s2.obsDate = '$END_DATE$' )
                        and DAYOFMONTH(g.obsDate) = 15
                        and g.obsDate between '$START_DATE$' and '$END_DATE$'
"""

ATL_TEMPLATE = """ SELECT 'id', 'obsDate', 'obstime', 'latitude', 'longitude'
                    union select id, obsDate, obstime, latitude, -1*longitude
                        into outfile '$PATH$/atl_drifters_$RANGE$_day_$END_DATE$.csv'
                        FIELDS TERMINATED BY ','
                        LINES TERMINATED BY '\\r\\n'
                    from gdpAtlAdj g
                    where exists (  select  1 from gdpAtlAdj s1
                                    where s1.id = g.id
                                        and     s1.obsDate = '$START_DATE$'
                                        and     s1.latitude >= 0
                                        and     s1.latitude <= 60
                                        and     s1.longitude between 0 and 90
                                    )
                        and exists ( select 1 from gdpAtlAdj s2
                                    where s2.id = g.id
                                        and s2.obsDate = '$END_DATE$' )
                        and DAYOFMONTH(g.obsDate) = 15
                        and g.obsDate between '$START_DATE$' and '$END_DATE$'
"""


def exportCohorts(cohorts, ocean='pacific'):
    conn = connection.new()

    if ocean.lower() == 'atlantic':
        sql = ATL_TEMPLATE
    else:
        sql = PAC_TEMPLATE

    for cohort in cohorts:
        startDate = cohort[0]
        endDate = cohort[1]
        timeRange = str(cohort[2])

        query = sql.replace('$START_DATE$', startDate).replace('$END_DATE$', endDate).replace('$RANGE$', timeRange).replace('$PATH$', "/tmp")
        #print query
        utils.executeMysql_All(conn, query)


# what percent of drifters die after X number of days
if __name__ == '__main__':
    cohorts = [("2004-02-25", "2005-03-31", 400),
                ("2003-01-21", "2005-03-31", 800),
                ("2006-02-25", "2007-03-31", 400),
                ("2005-01-21", "2007-03-31", 800),
                ("2008-02-25", "2009-03-31", 400),
                ("2008-01-21", "2009-03-31", 800),
                ("2010-02-25", "2011-03-31", 400),
                ("2009-01-21", "2011-03-31", 800)]

    #exportCohorts(cohorts, 'pacific')
    exportCohorts(cohorts, 'atlantic')
