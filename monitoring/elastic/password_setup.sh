#!/bin/bash

# resets and regenerate (-i) the password to an auto-generated value.
./bin/elasticsearch-reset-password -i -u elastic <<EOF
$ELASTIC_PASSWORD
EOF

./bin/elasticsearch-reset-password -i -u kibana_system <<EOF
$KIBANA_PASSWORD
EOF
