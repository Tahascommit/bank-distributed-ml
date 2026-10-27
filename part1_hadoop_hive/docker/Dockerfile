# One image for the whole mini cluster: the official Hive image already contains Hadoop 3.4.1.
# We add:
#   - the HDFS web files, which the Hive image leaves out (the namenode/datanode won't start without them)
#   - python3, so MapReduce jobs can be written in Python (Hadoop Streaming)
#   - Java 11 for the Hadoop daemons (Hadoop 3.4 supports Java 8/11, the image only has Java 21 for Hive)
#   - /data owned by the hive user, for the HDFS namenode/datanode storage

# stage 1: take share/hadoop/hdfs/webapps from the official Hadoop 3.4.1 release (checksum verified)
FROM apache/hive:4.2.1 AS hadoop-webapps
USER root
WORKDIR /tmp
ARG HADOOP_URL=https://archive.apache.org/dist/hadoop/common/hadoop-3.4.1/hadoop-3.4.1-lean.tar.gz
RUN curl -fsSL -o hadoop.tar.gz "$HADOOP_URL" \
 && curl -fsSL -o hadoop.tar.gz.sha512 "$HADOOP_URL.sha512" \
 && echo "$(awk '{print $NF}' hadoop.tar.gz.sha512)  hadoop.tar.gz" | sha512sum -c - \
 && tar -xzf hadoop.tar.gz hadoop-3.4.1/share/hadoop/hdfs/webapps \
 && rm hadoop.tar.gz

FROM apache/hive:4.2.1
USER root
RUN microdnf install -y python3 procps-ng hostname java-11-openjdk-headless && microdnf clean all \
 && mkdir -p /data/namenode /data/datanode && chown -R hive:hive /data
COPY --from=hadoop-webapps /tmp/hadoop-3.4.1/share/hadoop/hdfs/webapps /opt/hadoop/share/hadoop/hdfs/webapps
USER hive
