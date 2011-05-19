. "Tools/bash/_common.sh"
CONFIGURATION_FILE="${ASSETS_PROJECT}/config/gen/main.yaml"
java -jar "$TEXT_EXTRACTION_PROJECT}/build/text_extraction_server.jar" &
java -jar "${MESSAGE_QUEUE_PROJECT}/build/message_queue_server.jar" &
java -jar "${NOTIFICATION_PROJECT}/build/notification_server.jar" &
python "${MODEL_MANAGEMENT_PROJECT}/src/topic_tracking/model_management/app/story_updating_app.py" $CONFIGURATION_FILE &