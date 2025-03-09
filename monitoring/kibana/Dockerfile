FROM docker.elastic.co/kibana/kibana:8.17.0

# set environment variables for elastic connection
#ENV ELASTICSEARCH_HOSTS="http://elasticsearch:9200"

COPY kibana.yml /usr/share/kibana/config


CMD ["kibana"]
