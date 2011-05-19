SET ASSETS_PROJECT=%CD%/Assets
SET EVALUATION_PROJECT=%CD%/Evaluation
SET JAVA_COMMONS_PROJECT=%CD%/JavaCommons
SET MESSAGE_QUEUE_PROJECT=%CD%/MessageQueue
SET MODEL_MANAGEMENT_PROJECT=%CD%/ModelManagement
SET NOTIFICATION_PROJECT=%CD%/Notification
SET PROCESSING_PROJECT=%CD%/Processing
SET PYTHON_COMMONS_PROJECT=%CD%/PythonCommons
SET SEARCH_PROJECT=%CD%/Search
SET SIMILARITY_PROJECT=%CD%/Similarity
SET TEXT_EXTRACTION_PROJECT=%CD%/TextExtraction
SET TOPIC_MANAGEMENT_PROJECT=%CD%/TopicManagement
SET TOOLS_PROJECT=%CD%/Tools
SET WEB_PROJECT=%CD%/Web
SET EXTERNAL=%CD%/external


:: Python path
IF NOT DEFINED PYTHONPATH ^
SET PYTHONPATH=^
%EVALUATION_PROJECT%/src;^
%MODEL_MANAGEMENT_PROJECT%/src;^
%PROCESSING_PROJECT%/src;^
%PYTHON_COMMONS_PROJECT%/src;^
%TOOLS_PROJECT%/src;^
%TOPIC_MANAGEMENT_PROJECT%/src;^
%WEB_PROJECT%/src;^
%EXTERNAL%/python/lib


:: Java class path
SET CLASSPATH=%CD%/Search/build/*