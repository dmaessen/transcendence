FROM docker.elastic.co/beats/filebeat:8.17.0

COPY filebeat.yml /usr/share/filebeat/filebeat.yml

# for permissions
USER root

# atart with permissions disabled
CMD ["filebeat", "run", "-e", "--strict.perms=false"]
