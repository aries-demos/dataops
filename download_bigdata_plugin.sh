#!/usr/bin/env bash

#at assets.example.com server
#tispark
#https://github.com/RedisLabs/spark-redis
#https://github.com/mongodb/mongo-spark
#https://github.com/datastax/spark-cassandra-connector
#https://github.com/apache/carbondata
#https://github.com/hortonworks-spark/spark-atlas-connector
#uber hudi

base_dir=/data/assets/share

mkdir -p $base_dir/{spark,hive,presto,storm,flink,hadoop,hbase,kafkaconnector}

wget  http://repo1.maven.org/maven2/com/redislabs/spark-redis/2.3.1-m3/spark-redis-2.3.1-m3-jar-with-dependencies.jar -P $base_dir/spark/
wget  http://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.11/2.4.0/mongo-spark-connector_2.11-2.4.0.jar -P $base_dir/spark/
wget  http://download.pingcap.org/tispark-latest-linux-amd64.tar.gz -O /tmp/tispark-latest-linux-amd64.tar.gz && cd /tmp && tar -zxvf tispark-latest-linux-amd64.tar.gz && mv core/target/tispark-core-*-jar-with-dependencies.jar $base_dir/spark/
wget  http://mirrors.aliyun.com/apache/carbondata/1.5.2/apache-carbondata-1.5.2-bin-spark2.3.2-hadoop2.7.2.jar -P $base_dir/spark/
wget  http://mirrors.aliyun.com/apache/carbondata/1.5.2/apache-carbondata-1.5.2-bin-spark2.3.2-hadoop2.7.2.jar -P $base_dir/presto/
wget  http://dl.bintray.com/spark-packages/maven/datastax/spark-cassandra-connector/2.4.0-s_2.11/:spark-cassandra-connector-2.4.0-s_2.11.jar  -P $base_dir/spark/
wget  https://repo1.maven.org/maven2/com/intel/analytics/zoo/analytics-zoo-bigdl_0.7.2-spark_2.4.0/0.4.0/analytics-zoo-bigdl_0.7.2-spark_2.4.0-0.4.0-jar-with-dependencies-and-spark.jar -P $base_dir/spark/

wget  http://repo1.maven.org/maven2/com/uber/hoodie/hoodie-spark-bundle/0.4.5/hoodie-spark-bundle-0.4.5.jar -P $base_dir/spark/
wget  http://repo1.maven.org/maven2/com/uber/hoodie/hoodie-hive-bundle/0.4.5/hoodie-hive-bundle-0.4.5.jar -P $base_dir/hive/
wget  http://repo1.maven.org/maven2/com/uber/hoodie/hoodie-hadoop-mr-bundle/0.4.5/hoodie-hadoop-mr-bundle-0.4.5.jar -P $base_dir/hive/
wget  http://repo1.maven.org/maven2/com/uber/hoodie/hoodie-presto-bundle/0.4.5/hoodie-presto-bundle-0.4.5.jar $base_dir/presto/
wget  https://github.com/xiaomatech/jars/raw/master/spark-authorizer-2.1.1.jar -P $base_dir/spark/
wget  https://github.com/xiaomatech/jars/raw/master/spark-atlas-connector_2.11-0.1.0-SNAPSHOT.jar -P $base_dir/spark/


elk_version=7.0.0
wget https://artifacts.elastic.co/downloads/elasticsearch-hadoop/elasticsearch-hadoop-$elk_version.zip -O /tmp/elasticsearch-hadoop-$elk_version.zip
cd /tmp
unzip elasticsearch-hadoop-$elk_version.zip
mv elasticsearch-hadoop-$elk_version/dist/elasticsearch-hadoop-$elk_version.jar $base_dir/hadoop/
mv elasticsearch-hadoop-$elk_version/dist/elasticsearch-hadoop-mr-$elk_version.jar $base_dir/hadoop/
mv elasticsearch-hadoop-$elk_version/dist/elasticsearch-hadoop-hive-$elk_version.jar $base_dir/hive/
mv elasticsearch-hadoop-$elk_version/dist/elasticsearch-spark-20_2.11-$elk_version.jar $base_dir/spark/
mv elasticsearch-hadoop-$elk_version/dist/elasticsearch-storm-$elk_version.jar $base_dir/storm/

#kafkaconnector
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-mysql/0.9.4.Final/debezium-connector-mysql-0.9.4.Final-plugin.tar.gz $base_dir/kafkaconnector/
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/0.9.4.Final/debezium-connector-postgres-0.9.4.Final-plugin.tar.gz $base_dir/kafkaconnector/
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-mongodb/0.9.4.Final/debezium-connector-mongodb-0.9.4.Final-plugin.tar.gz $base_dir/kafkaconnector/


wget http://repo1.maven.org/maven2/com/yahoo/datasketches/sketches-hive/0.13.0/sketches-hive-0.13.0-with-shaded-core.jar -P $base_dir/hive/
