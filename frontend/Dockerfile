FROM nginx:alpine

RUN apk update && apk add --no-cache bash curl wget git bc netcat-openbsd openssl

# Copy static files to Nginx HTML directory

RUN rm /etc/nginx/conf.d/default.conf
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

RUN		mkdir /etc/nginx/certs \
	&&	openssl req	-x509 \
					-nodes \
					-days 365 \
					-newkey rsa:2048 \
					-keyout /etc/nginx/certs/privkey.pem \
					-out	/etc/nginx/certs/fullchain.pem \
					-subj	"/C=NL/ST=NH/L=AMS/O=CODAM/OU=Student/CN=avon-ben.42.fr"

COPY ../static /usr/share/nginx/html
# COPY ../static/templates /usr/share/nginx/html/static/templates
# COPY ../static/frontend /usr/share/nginx/html/static/frontend
# COPY ../js/* /usr/share/nginx/html

RUN chmod -R 755 /usr/share/nginx/html

# Expose Nginx port
EXPOSE 443

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
