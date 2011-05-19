:: Variables:
:: Required: ES_HOME
:: Optional: DEBUG_OPTS


@ECHO OFF


:: Set up common properties
CALL "%CD%/Tools/batch/_common.bat"


:: Prepare elasticsearch

SET JAVA_OPTS=%DEBUG_OPTS%^
 -Xms256m^
 -Xmx1G^
 -Djline.enabled=false^
 -XX:+AggressiveOpts^
 -XX:+UseParNewGC^
 -XX:+UseConcMarkSweepGC^
 -XX:+CMSParallelRemarkEnabled^
 -XX:+HeapDumpOnOutOfMemoryError

SET ES_CLASSPATH=%CLASSPATH%;%ES_HOME%/lib/elasticsearch-0.16.0.jar;%ES_HOME%/lib/*;%ES_HOME%/lib/sigar/*
SET ES_PARAMS=-Delasticsearch -Des-foreground=yes -Des.path.home="%ES_HOME%" -Des.path.conf="%SEARCH_PROJECT%/elasticsearch/config"

START "elasticsearch" "%JAVA_HOME%/bin/java" %JAVA_OPTS% %ES_JAVA_OPTS% %ES_PARAMS% -cp "%ES_CLASSPATH%" "org.elasticsearch.bootstrap.Bootstrap"