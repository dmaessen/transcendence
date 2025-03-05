FROM docker.elastic.co/elasticsearch/elasticsearch:8.17.0

# set environment variables for security configuration
ENV discovery.type=single-node \
    ES_JAVA_OPTS="-Xms512m -Xmx512m"
    #xpack.security.enabled=false

# RUN apt-get update
# RUN apt-get install -y mkcert


RUN mkdir -p /usr/share/elasticsearch


COPY elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
COPY certs.sh /usr/share/elasticsearch
COPY password_setup.sh /usr/share/elasticsearch

USER root
RUN chmod 777 /usr/share/elasticsearch/certs.sh
RUN chmod 777 /usr/share/elasticsearch/password_setup.sh

RUN chmod 777 /usr/share/elasticsearch/config/users
RUN /usr/share/elasticsearch/config/users useradd ${ELASTICSEARCH_USER} -p ${ELASTIC_PASSWORD} -r superuser,kibana_system

#RUN /usr/share/elasticsearch/password_setup.sh

USER elasticsearch

RUN /usr/share/elasticsearch/certs.sh

# to start Elasticsearch
CMD ["elasticsearch"]
