#!/bin/bash


#Applying ILM policy
curl -k -u $ELASTIC_USERNAME:$ELASTIC_PASSWORD -X PUT "$ELASTIC_HOSTS/_ilm/policy/logs-lifecycle-policy" -H 'Content-Type: application/json' -d @ilm-policy.json

#Applying Index Template
curl -k -u $ELASTIC_USERNAME:$ELASTIC_PASSWORD -X PUT "$ELASTIC_HOSTS/_index_template/universal-logs-template" -H 'Content-Type: application/json' -d @index-template.json

patterns=(
  "backend-django_utils_autoreload-logs-*"
  "backend-django_channels_server-logs-*"
  "backend-django_request-logs-*"
  "frontend-nginx_access-logs-*"
  "frontend-nginx_error-logs-*"
)


for pattern in "${patterns[@]}"; do
    #Pull all indices according to the pattern above
  indices=$(curl -k -u $ELASTIC_USERNAME:$ELASTIC_PASSWORD -X GET "$ELASTIC_HOSTS/_cat/indices?h=index" | grep -E "$pattern")

    #Apply ilm for each of them, during the eval change time and storage values
  for index in $indices; do
    echo "➡️ Applying ILM policy and alias to index: $index"
    curl -k -u $ELASTIC_USERNAME:$ELASTIC_PASSWORD -X PUT "$ELASTIC_HOSTS/$index/_settings" -H 'Content-Type: application/json' -d '{
      "settings": {
        "index.lifecycle.name": "logs-lifecycle-policy",
        "index.lifecycle.rollover_alias": "universal-logs-write"
      }
    }'
    curl -k -u $ELASTIC_USERNAME:$ELASTIC_PASSWORD -X POST "$ELASTIC_HOSTS/$index/_alias/universal-logs-write" -H 'Content-Type: application/json' -d '{
      "is_write_index": true
    }'
    echo -e "ILM policy and alias applied to $index.\n"
  done
done


echo "ILM done!"
