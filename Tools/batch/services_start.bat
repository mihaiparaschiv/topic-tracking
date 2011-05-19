@ECHO OFF


:: Set up common properties
CALL "%CD%/Tools/batch/_common.bat"


SET CONFIGURATION_FILE=%ASSETS_PROJECT%/config/gen/main.yaml


START "TextExtraction Service" java -jar "%TEXT_EXTRACTION_PROJECT%/build/text_extraction_server.jar"
START "MessageQueue Service" java -jar "%MESSAGE_QUEUE_PROJECT%/build/message_queue_server.jar"
:: START "Notification Service" java -jar "%NOTIFICATION_PROJECT%/build/notification_server.jar"

START "Processing Service" python "%PROCESSING_PROJECT%/src/topic_tracking/processing/app/processing_service.py" "%CONFIGURATION_FILE%"
START "Story Updating Service" python "%MODEL_MANAGEMENT_PROJECT%/src/topic_tracking/model_management/app/story_updating_app.py" "%CONFIGURATION_FILE%"
:: START "TopicManagement Service" python "%TOPIC_MANAGEMENT_PROJECT%/src/topic_tracking/topic_management/app/topic_management_app.py" "%CONFIGURATION_FILE%"


ECHO Services started