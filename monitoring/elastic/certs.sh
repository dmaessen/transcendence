#!/bin/bash

# manually generates and manages SSL/TLS certificates using OpenSSL

CERT_DIR="/usr/share/elasticsearch/config/cert"

mkdir -p $CERT_DIR

#NOTES:
# .p12 .pem are certificate formats


#touch $CERT_DIR/ca_cert.srl

#CA
openssl genpkey -algorithm RSA -out $CERT_DIR/ca_private_key.pem
openssl req -x509 -new -key $CERT_DIR/ca_private_key.pem -days 365 -out $CERT_DIR/ca_cert.crt -subj "/CN=elasticsearch"

if [ ! -f "$CERT_DIR/ca_cert.srl" ]; then
    echo 01 > $CERT_DIR/ca_cert.srl
fi

#elastic private key
openssl genpkey -algorithm RSA -out $CERT_DIR/elastic_key.pem
# File permission chmod 777 for private keys.
chmod 777 $CERT_DIR/elastic_key.pem
#Certificate Signing Request (CSR) (*_csr.crt)
openssl req -new -key $CERT_DIR/elastic_key.pem -out $CERT_DIR/elastic_csr.crt -subj "/CN=elasticsearch"
# A signed certificate (*_cert_signed.crt).
# Certificates are signed using the previously generated CA.
openssl x509 -req -in $CERT_DIR/elastic_csr.crt -CA $CERT_DIR/ca_cert.crt -CAkey $CERT_DIR/ca_private_key.pem -days 365 -out $CERT_DIR/elastic_cert_signed.crt


openssl genpkey -algorithm RSA -out $CERT_DIR/logstash_key.pem
chmod 777 $CERT_DIR/logstash_key.pem
openssl req -new -key $CERT_DIR/logstash_key.pem -out $CERT_DIR/logstash_csr.crt -subj "/CN=elasticsearch"
openssl x509 -req -in $CERT_DIR/logstash_csr.crt -CA $CERT_DIR/ca_cert.crt -CAkey $CERT_DIR/ca_private_key.pem -days 365 -out $CERT_DIR/logstash_cert_signed.crt

#kibana
openssl genpkey -algorithm RSA -out $CERT_DIR/kibana_key.pem
chmod 777 $CERT_DIR/kibana_key.pem
openssl req -new -key $CERT_DIR/kibana_key.pem -out $CERT_DIR/kibana_csr.crt -subj "/CN=elasticsearch"
openssl x509 -req -in $CERT_DIR/kibana_csr.crt -CA $CERT_DIR/ca_cert.crt -CAkey $CERT_DIR/ca_private_key.pem -days 365 -out $CERT_DIR/kibana_cert_signed.crt

#filebeat
openssl genpkey -algorithm RSA -out $CERT_DIR/filebeat_key.pem
chmod 777 $CERT_DIR/filebeat_key.pem
openssl req -new -key $CERT_DIR/filebeat_key.pem -out $CERT_DIR/filebeat_csr.crt -subj "/CN=elasticsearch"
openssl x509 -req -in $CERT_DIR/filebeat_csr.crt -CA $CERT_DIR/ca_cert.crt -CAkey $CERT_DIR/ca_private_key.pem -days 365 -out $CERT_DIR/filebeat_cert_signed.crt

#exec /usr/share/elasticsearch/password_setup.sh