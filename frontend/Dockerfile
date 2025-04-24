FROM nginx:alpine

# Copy static files to Nginx HTML directory

RUN rm /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/conf.d/default.conf


COPY . /usr/share/nginx/html
# COPY ../js/* /usr/share/nginx/html

# Expose Nginx port
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
