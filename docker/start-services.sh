#!/bin/bash

/usr/bin/zookeeper-server-start.sh /etc/kafka/zookeeper.properties &
while ss -ltn | awk '$4 ~ /:2181$/ {exit 1}'; do sleep 10; done

/usr/bin/kafka-server-start.sh /etc/kafka/server.properties &
while ss -ltn | awk '$4 ~ /:9092$/ {exit 1}'; do sleep 10; done

sudo -u user bci-framework
