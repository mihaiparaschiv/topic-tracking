@ECHO OFF


:: Set up common properties
CALL "%CD%/Tools/batch/_common.bat"


SET CONFIGURATION_FILE=%ASSETS_PROJECT%/config/gen/main.yaml


START "Processing" python "%PROCESSING_PROJECT%/src/topic_tracking/processing/app/processing_app.py" "%CONFIGURATION_FILE%"
START "Processed resource handling" python "%MODEL_MANAGEMENT_PROJECT%/src/topic_tracking/model_management/app/processed_resource_handling_app.py" "%CONFIGURATION_FILE%"


ECHO Applications started