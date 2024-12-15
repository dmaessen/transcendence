FROM nginx:alpine

# Copy static files to Nginx HTML directory
#COPY ./statics/* /usr/share/nginx/html/static

COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# COPY ../js/* /usr/share/nginx/html

# Expose Nginx port
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
