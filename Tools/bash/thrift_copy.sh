rm -fr $JAVA_COMMONS_PROJECT/src/topicTracking/service/*
rm -fr $PYTHON_COMMONS_PROJECT/src/topic_tracking/service/*
cp -R $ASSETS_PROJECT/thrift/gen-java/topicTracking/service $JAVA_COMMONS_PROJECT/src/topicTracking
cp -R $ASSETS_PROJECT/thrift/gen-py/topic_tracking/service $PYTHON_COMMONS_PROJECT/src/topic_tracking

