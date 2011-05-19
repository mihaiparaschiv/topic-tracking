:: Variables:
:: Required: ES_HOME, CONFIGURATION_FILE, SETTINGS_FILE


@ECHO OFF


:: Set up common properties
CALL "%CD%/Tools/batch/_common.bat"


SET /p answer="Type Y for reset. "
IF /i "%answer%" EQU "Y" GOTO:reset_data


ECHO No changes were made.
GOTO:eof


:reset_data
    
    ECHO Deleting folders...
    RD /S /Q "%ES_HOME%/data"
    RD /S /Q "%ES_HOME%/logs"
    
    ECHO Start ElasticSearch!
    SET /p _="Press any key after ElasticSearch has loaded... "
    
    ECHO Setting up ElasticSearch...
    START /B "set_up_elasticsearch" python ^
    "%TOOLS_PROJECT%/src/topic_tracking/tools/set_up_elasticsearch.py" ^
    "%CONFIGURATION_FILE%" "%SETTINGS_FILE%"
    
    ECHO Data reset.