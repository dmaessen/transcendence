FROM docker.elastic.co/logstash/logstash:8.17.0

COPY logstash.conf /usr/share/logstash/pipeline/

# ownership and permissions, not sure if necessary? user is already logstash
# USER logstash

# start
CMD ["logstash", "-f", "/usr/share/logstash/pipeline/logstash.conf"]
