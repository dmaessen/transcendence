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
            "max_age": "10m",
            "max_docs": 10000
          }
        }
      },
      "delete": {
        "min_age": "20m",
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

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X PUT "https://elasticsearch:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "indices.lifecycle.poll_interval": "2m" 
  }
}'

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "https://elasticsearch:9200/logs-generic-default/_rollover"

sleep 2

curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "https://elasticsearch:9200/logs-generic-default/_rollover"



exec /usr/local/bin/kibana-docker


# #!/bin/bash

# sleep 30

# # ILM politikası oluşturma
# curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X PUT "https://elasticsearch:9200/_ilm/policy/logs-policy" -H 'Content-Type: application/json' -d'
# {
#   "policy": {
#     "phases": {
#       "hot": {
#         "min_age": "0ms",
#         "actions": {
#           "rollover": {
#             "max_age": "2m",
#             "max_docs": 100
#           }
#         }
#       },
#       "delete": {
#         "min_age": "4m",
#         "actions": {
#           "delete": {}
#         }
#       }
#     }
#   }
# }'

# # Index template oluşturma
# curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X PUT "https://elasticsearch:9200/_index_template/logs-template" -H 'Content-Type: application/json' -d'
# {
#   "index_patterns": ["logs-*-*"],
#   "data_stream": { },
#   "priority": 500,
#   "template": {
#     "settings": {
#       "index.lifecycle.name": "logs-policy"
#     }
#   }
# }'

# sleep 10

# # İlk oluşturulan data stream index'ini `logs-policy` ILM politikasına bağla
# FIRST_INDEX=$(curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -s "https://elasticsearch:9200/_data_stream/logs-generic-default" | jq -r '.data_streams[0].indices[0].index_name')

# curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X PUT "https://elasticsearch:9200/${FIRST_INDEX}/_settings" -H 'Content-Type: application/json' -d'
# {
#   "index.lifecycle.name": "logs-policy"
# }'

# # Rollover işlemini tetikle
# curl -k -u "${ELASTIC_USERNAME}:${ELASTIC_PASSWORD}" -X POST "https://elasticsearch:9200/logs-generic-default/_rollover"

# exec /usr/local/bin/kibana-docker



