                    (id
                    ,obsDateTime
                    ,obsDate
                    ,obsTime
                    ,latitude
                    ,longitude
                    ,longitudeWest
                    ,sst
                    ,ewct
                    ,nsct
                    ,latError
                    ,longError
                    ,origExpNum
                    ,wmoPlatform
                    ,hasDrogue)
    select          id
                    ,obsDate
                    ,date(obsDate) as obsDate
                    ,time(obsDate) as obsTime
                    ,latitude
                    ,longitude
                    ,-1.0 * longitude as longitudeWest
                    ,sst
                    ,ewct
                    ,nsct
                    ,latError
                    ,longError
                    ,origExpNum
                    ,wmoPlatform
                    ,hasDrogue
    from            gdpPac$$number
    order by        id
                    ,obsDate;