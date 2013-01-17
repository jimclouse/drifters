import ConfigParser
import utils

_config = ConfigParser.RawConfigParser()
_config.read("config.cfg")


def new():
    return utils.getMysqlConnection(_config.get("db", "host"),
                                    _config.get("db", "username"),
                                    _config.get("db", "password"),
                                    _config.get("db", "database"))
