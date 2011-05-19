@ECHO OFF


:: Set up common properties
CALL "%CD%/Tools/batch/_common.bat"


ROBOCOPY /E /NP /NJS "%ASSETS_PROJECT%/thrift/gen-java/topicTracking/service" ^
"%JAVA_COMMONS_PROJECT%/src/topicTracking/service"


ROBOCOPY /E /NP /NJS "%ASSETS_PROJECT%/thrift/gen-py/topic_tracking/service" ^
"%PYTHON_COMMONS_PROJECT%/src/topic_tracking/service"