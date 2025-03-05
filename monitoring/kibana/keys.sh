#!/bin/bash

./bin/kibana-keystore create

#Add the password for the kibana_system user to the Kibana keystore
#enter the password for the kibana_system user
./bin/kibana-keystore add elasticsearch.password <<EOF
$KIBANA_PASSWORD
EOF


# Start Kibana
exec /usr/local/bin/kibana-docker