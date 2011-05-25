cd $ASSETS_PROJECT; pwd
cd thrift/src/ ;pwd

echo Generating thrift files

list=`ls *.thrift`

for x in $list
do
  for y in java py:utf8strings
  do
    #echo $ASSETS_PROJECT/thrift
    thrift -o $ASSETS_PROJECT/thrift --gen $y $x
  done
done

