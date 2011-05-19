@ECHO OFF


PUSHD output
PUSHD logs

DEL /P *.log

ECHO Logs deleted.

POPD
POPD