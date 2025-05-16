FROM nginx:alpine

RUN apk update && apk add --no-cache bash curl wget openssl

RUN rm /etc/nginx/conf.d/default.conf
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

RUN apk add --no-cache nss-tools \
    && wget -O /usr/local/bin/mkcert https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64 \
    && chmod +x /usr/local/bin/mkcert \
    && mkcert -install \
    && mkdir -p /etc/nginx/certs \
    && mkcert -cert-file /etc/nginx/certs/fullchain.pem -key-file /etc/nginx/certs/privkey.pem tranceanddance.com

# RUN mkdir /etc/nginx/certs \
#     && openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
#     -keyout /etc/nginx/certs/privkey.pem \
#     -out /etc/nginx/certs/fullchain.pem \
#     -subj "/C=NL/ST=NH/L=AMS/O=CODAM/OU=Student/CN=localhost"

COPY ../static /usr/share/nginx/html/static/
COPY ../media /usr/share/nginx/html/media/

RUN chmod -R 755 /usr/share/nginx/html

# EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]

# FROM nginx:alpine

# RUN apk update && apk add --no-cache bash curl wget git bc netcat-openbsd openssl

# # Copy static files to Nginx HTML directory

# RUN rm /etc/nginx/conf.d/default.conf
# COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# RUN		mkdir /etc/nginx/certs \
# 	&&	openssl req	-x509 \
# 					-nodes \
# 					-days 365 \
# 					-newkey rsa:2048 \
# 					-keyout /etc/nginx/certs/privkey.pem \
# 					-out	/etc/nginx/certs/fullchain.pem \
# 					-subj	"/C=NL/ST=NH/L=AMS/O=CODAM/OU=Student/CN=avon-ben.42.fr"

# COPY ../static /usr/share/nginx/html
# # COPY ../static/templates /usr/share/nginx/html/static/templates
# # COPY ../static/frontend /usr/share/nginx/html/static/frontend
# # COPY ../js/* /usr/share/nginx/html

# RUN chmod -R 755 /usr/share/nginx/html

# # Expose Nginx port
# EXPOSE 443

# # Start Nginx server
# CMD ["nginx", "-g", "daemon off;"]
