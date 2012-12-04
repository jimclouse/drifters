import utils
import ConfigParser
from datetime import date
from time import strftime
from datetime import timedelta
import csv


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days / 7)):
        yield start_date + timedelta(n * 7)


def writeDriftersToFile(exportDate, drifters):
    f = open("../data/drifters/drifters_" + exportDate.replace("-", "_") + ".txt", "w")
    writer = csv.writer(f)
    writer.writerow(["Id", "obsDateTime", "obsDate", "obsTime", "latitude", "longitude", "longitudeWest", "hasDrogue"])
    for row in drifters:
        rowId = row.get("id")
        # TODO - add all these to a list and run a loop: 7 lines into 2
        obsDateTime = row.get("obsDateTime")
        obsDate = row.get("obsDate")
        obsTime = row.get("obsTime")
        latitude = row.get("latitude")
        longitude = row.get("longitude")
        longitudeWest = row.get("longitudeWest")
        hasDrogue = row.get("hasDrogue")
        writer.writerow([rowId, obsDateTime, obsDate, obsTime, latitude, longitude, longitudeWest, hasDrogue])


def main():
    utils.mkdir("../data/drifters")
    _config = ConfigParser.RawConfigParser()
    _config.read("config.cfg")

    conn = utils.getMysqlConnection(_config.get("db", "host"),
                                    _config.get("db", "username"),
                                    _config.get("db", "password"),
                                    _config.get("db", "database"))

    sqlDrifterExport = """ SELECT id, obsDateTime, obsDate, obsTime, latitude, longitude, longitudeWest, hasDrogue
                        from gdpAll where obsTime = '6:00' and obsDate = '$$date'
                        and latitude between 15 and 40 and longitude <= 82 and longitude >= 31;"""

    start_date = date(2008, 12, 4)
    end_date = date(2009, 4, 30)

    for single_date in daterange(start_date, end_date):
        exportDate = strftime("%Y-%m-%d", single_date.timetuple())
        sql = sqlDrifterExport.replace("$$date", exportDate)
        drifters = utils.executeMysql_All(conn, sql)
        writeDriftersToFile(exportDate, drifters)

if __name__ == '__main__':
    main()
