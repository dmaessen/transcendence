# Exit on Error
set -e

#Nice doc:
#https://www.elastic.co/guide/en/elasticsearch/reference/current/certutil.html

#OUTPUT_DIR=/usr/share/elasticsearch/credentials/certs
OUTPUT_DIR=/secrets/certs
ZIP_CA_FILE=$OUTPUT_DIR/ca.zip
ZIP_FILE=$OUTPUT_DIR/certs.zip

printf "======= Generating Elastic Stack Certificates =======\n"
printf "=====================================================\n"

if ! command -v unzip &>/dev/null; then
    printf "Installing Necessary Tools... \n"
    yum install -y -q -e 0 unzip;
fi

printf "Clearing Old Certificates if exits... \n"
mkdir -p $OUTPUT_DIR
find $OUTPUT_DIR -type d -exec rm -rf -- {} +
mkdir -p $OUTPUT_DIR/ca


printf "Generating CA Certificates... \n"
PASSWORD=`openssl rand -base64 32`
/usr/share/elasticsearch/bin/elasticsearch-certutil ca --pass "$PASSWORD" --pem --out $ZIP_CA_FILE &> /dev/null
printf "Generating Certificates... \n"
unzip -qq $ZIP_CA_FILE -d $OUTPUT_DIR;
/usr/share/elasticsearch/bin/elasticsearch-certutil cert --silent --pem  --ca-cert $OUTPUT_DIR/ca/ca.crt --ca-key $OUTPUT_DIR/ca/ca.key --ca-pass "$PASSWORD" --in /scripts/instances.yml -out $ZIP_FILE  &> /dev/null

printf "Unzipping Certifications... \n"
unzip -qq $ZIP_FILE -d $OUTPUT_DIR;

# #COPY THINGS TO CONFIG
# cp -rf $OUTPUT_DIR /usr/share/elasticsearch/config

printf "Applying Permissions... \n"
chown -R 1000:0 $OUTPUT_DIR
find $OUTPUT_DIR -type f -exec chmod 655 -- {} +

printf "=====================================================\n"
printf "SSL Certifications generation completed successfully.\n"
printf "=====================================================\n"

