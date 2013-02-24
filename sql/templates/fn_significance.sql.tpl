DROP FUNCTION IF EXISTS fn_significance;
GO
delimiter //
CREATE FUNCTION fn_significance(testStat float, pvalue float)
RETURNS varchar(32)
BEGIN

declare sig varchar(4);
declare result varchar(28);

set sig = case when pvalue >= 0.05 then '' 
                when pvalue < 0.05 and pvalue >=0.01 then '*'
                when pvalue < 0.01 and pvalue >=0.001 then '**'
                when pvalue < 0.001 and pvalue >=0.0001 then '***'
                when pvalue < 0.0001 then '****' END;


set result = concat(trim(cast(testStat as char(28))), sig);

RETURN result;

END//

delimiter ;