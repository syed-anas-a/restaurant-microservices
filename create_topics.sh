#!/usr/bin/env bash
set -e

docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --if-not-exists --topic order.placed --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092

docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --if-not-exists --topic delivery.status_changed --partitions 3 --replication-factor 1 --bootstrap-server localhost:9092

docker exec kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092