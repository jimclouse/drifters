import MySQLdb
import MySQLdb.cursors
import logging
import os
import shutil
from logging.handlers import RotatingFileHandler
from warnings import filterwarnings
from warnings import resetwarnings

LOGGING_PATH = "./log"
ROOT_LOGGER_NAME = "ocean"
LOGGING_LEVEL = "DEBUG"
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data')
DATA_PATH_PAC = os.path.join(DATA_PATH, 'drifters', 'Pacific')
DATA_PATH_ATL = os.path.join(DATA_PATH, 'drifters', 'Atlantic')


def rmdir(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)


def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def delFile(fileName):
    if os.path.exists(fileName):
        os.remove(fileName)


def getLogger():
    """ determines if the root logger is set up by looking for its handlers.
    it is assumed that if there are no handlers, the logger is not set
    if no logger is set, the base logger will be instantiated
    """
    _newLogger = initRotatingLogger(ROOT_LOGGER_NAME, "output.log", LOGGING_PATH, True, True, LOGGING_LEVEL)
    return _newLogger


def initRotatingLogger(logName, fileName, logDir=None, toScreen=True, toText=True, logLevel=logging.INFO):
    logDir = os.path.abspath(logDir)
    mkdir(logDir)

    logger = logging.getLogger(logName)
    logger.setLevel(logLevel)

    log_formatter = logging.Formatter("%(asctime)s Log_Level=%(levelname)s Module=[%(name)s] %(message)s")

    if toText:
        txt_handler = RotatingFileHandler(os.path.join(logDir, fileName), maxBytes=1000000, backupCount=7)
        txt_handler.setFormatter(log_formatter)
        logger.addHandler(txt_handler)
        logger.debug("%s Logger initialized", logName)

    if toScreen:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
    return logger


""" ################
    MySQL Data utils
"""
def getMysqlConnection(host, user, pwd, db, sock=""):
    """ execute a mysql query and return results in a list
    """
    try:
        if sock == "":
            return MySQLdb.connect(host=str(host), user=str(user), passwd=str(pwd), db=str(db), cursorclass=MySQLdb.cursors.DictCursor)
        else:
            return MySQLdb.connect(unix_socket=str(sock), host=str(host), user=str(user), passwd=str(pwd), db=str(db), cursorclass=MySQLdb.cursors.DictCursor)
    except Exception as e:
        logger.error(str(e))
        raise Exception(str(e))


def executeMysql_All(connection, sqlQuery):
    """ mysql fetchall
    """
    try:
        cursor = connection.cursor()
        cursor.execute(sqlQuery)
        results = cursor.fetchall()
        cursor.close()
        return results
    except Exception as e:
        logger.error("Status=Failure Method='Mysql data query' Conn_Host=%s %s", str(connection.get_host_info()), str(e))
        raise Exception(str(e))


def executeMysql_One(connection, sqlQuery):
    """ mysql fetchone
    """
    try:
        filterwarnings('ignore', category=MySQLdb.Warning)
        cursor = connection.cursor()
        cursor.execute(sqlQuery)
        results = cursor.fetchone()
        cursor.close()
        mysqlProcessWarnings(connection, sqlQuery)
        return results
    except Exception as e:
        logger.error("Status=Failure Method='Mysql data query' Conn_Host=%s %s", str(connection.get_host_info()), str(e))
        raise Exception(str(e))
    finally:
        resetwarnings()


def executeMysql_Command(connection, sqlQuery):
    """ mysql command. execute statement and return number of results
    """
    try:
        filterwarnings('ignore', category=MySQLdb.Warning)
        _cursor = connection.cursor()
        _cursor.execute(sqlQuery)
        _rc = _cursor.rowcount
        mysqlProcessWarnings(connection, sqlQuery)
        _cursor.close()
        return _rc
    except Exception as e:
        logger.error("Status=Failure Method='Mysql data query' Conn_Host=%s %s", str(connection.get_host_info()), str(e))
        raise Exception(str(e))
    finally:
        resetwarnings()


def mysqlProcessWarnings(mysql_connection, originalSql):
    sql = "SHOW WARNINGS;"
    results = executeMysql_All(mysql_connection, sql)
    if len(results):
        logger.warning("%i warnings produced by query %s", len(results), originalSql)
        for warning in results:
            logger.warning("%s", warning)

logger = getLogger()
