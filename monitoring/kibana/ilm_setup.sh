#!/bin/bash

sleep 30

# ILM politikası oluşturma
curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X PUT "https://elasticsearch:9200/_ilm/policy/logs-policy" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "2m",
            "max_docs": 100
          }
        }
      },
      "delete": {
        "min_age": "4m",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X PUT "https://elasticsearch:9200/_index_template/logs-template" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["logs-*-*"],
  "data_stream": { },
  "priority": 500,
  "template": {
    "settings": {
      "index.lifecycle.name": "logs-policy"
    }
  }
}'

#curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X PUT "https://elasticsearch:9200/_data_stream/test-logs-default"

# Şu anki tarihi ISO formatında al
# CURRENT_DATE=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

# # Test log eklerken gerçek tarih kullan
# curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "https://elasticsearch:9200/logs-default/_doc" -H 'Content-Type: application/json' -d'
# {
#   "@timestamp": "'$CURRENT_DATE'",
#   "message": "Test log 1"
# }'

# curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "https://elasticsearch:9200/logs-default/_doc?refresh=true" -H 'Content-Type: application/json' -d'
# {
#   "@timestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"'",
#   "message": "Data stream initialized"
# }'
exec /usr/local/bin/kibana-docker
