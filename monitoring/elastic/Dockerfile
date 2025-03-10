FROM docker.elastic.co/elasticsearch/elasticsearch:8.17.0

# set environment variables for security configuration
# ENV discovery.type=single-node \
#     ES_JAVA_OPTS="-Xms512m -Xmx512m"
    #xpack.security.enabled=false

# RUN apt-get update
# RUN apt-get install -y mkcert


#RUN mkdir -p /usr/share/elasticsearch

# COPY elasticsearch.yml /usr/share/elasticsearch/config
# COPY log4j2.properties /usr/share/elasticsearch/config

# COPY keystore.sh /usr/share/elasticsearch
# COPY instances.yml /usr/share/elasticsearch
# COPY gen-cert.sh /usr/share/elasticsearch
# COPY bootstrap.sh /usr/share/elasticsearch
#COPY password_setup.sh /usr/share/elasticsearch

#USER root

#RUN mkdir -p /secrets
#RUN touch /credentials/.env.kibana.token

# RUN chmod 777 /usr/share/elasticsearch/keystore.sh \
#         /usr/share/elasticsearch/gen-cert.sh \
#         /usr/share/elasticsearch/bootstrap.sh
        # /credentials/.env.kibana.token


#RUN chmod 777 /usr/share/elasticsearch/config/users
#RUN /usr/share/elasticsearch/config/users useradd ${ELASTICSEARCH_USER} -p ${ELASTIC_PASSWORD} -r superuser,kibana_system

#RUN /usr/share/elasticsearch/password_setup.sh


# RUN /usr/share/elasticsearch/keystore.sh

# RUN /usr/share/elasticsearch/gen-cert.sh

#USER elasticsearch

# to start Elasticsearch
CMD ["elasticsearch"]
