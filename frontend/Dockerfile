FROM nginx:alpine

# Copy static files to Nginx HTML directory

RUN rm /etc/nginx/conf.d/default.conf
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf


COPY ../static /usr/share/nginx/html/static
# COPY ../js/* /usr/share/nginx/html

RUN chmod -R 755 /usr/share/nginx/html

# Expose Nginx port
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
