@ECHO OFF


:: Set up common properties
CALL "%CD%/Tools/batch/_common.bat"


SET CONFIGURATION_FILE=%ASSETS_PROJECT%/config/gen/main.yaml


START "Web server" python "%WEB_PROJECT%/src/topic_tracking_web/manage.py" runserver


ECHO Web server started