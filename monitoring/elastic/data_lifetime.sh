set -e

# Wait for elastic container
sleep 30



echo "Index Lifetime Policy settings..."
curl -k --user "elastic:$ELASTIC_PASSWORD" -X PUT https://localhost:9200/_ilm/policy/logs-lifecycle-policy \
  -H 'Content-Type: application/json' \
  -d '{
    "policy": {
      "phases": {
        "hot": {
          "actions": {
            "rollover": {
              "max_age": "1m",
              "max_size": "50gb"
            }
          }
        },
        "delete": {
          "min_age": "2m",
          "actions": {
            "delete": {}
          }
        }
      }
    }
  }'

exec /usr/local/bin/docker-entrypoint.sh elasticsearch