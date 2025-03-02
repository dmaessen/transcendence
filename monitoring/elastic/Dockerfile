FROM docker.elastic.co/elasticsearch/elasticsearch:8.17.0

# set environment variables for security configuration
ENV discovery.type=single-node \
    ES_JAVA_OPTS="-Xms512m -Xmx512m" \
    xpack.security.enabled=false


# to start Elasticsearch
CMD ["elasticsearch"]
